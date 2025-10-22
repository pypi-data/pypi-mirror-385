import os
import tqdm
import argparse
import traceback
import numpy as np
import pandas as pd
import multiprocessing as mp
from pathlib import Path

from slide2vec.utils import load_csv, fix_random_seeds
from slide2vec.utils.config import get_cfg_from_file
from slide2vec.wsi import extract_coordinates, save_coordinates, visualize_coordinates


def get_args_parser(add_help: bool = True):
    parser = argparse.ArgumentParser("slide2vec", add_help=add_help)
    parser.add_argument(
        "--config-file", default="", metavar="FILE", help="path to config file"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="",
        help="Name of output subdirectory",
    )
    return parser


def process_slide_wrapper(kwargs):
    return process_slide(**kwargs)


def process_slide(
    *,
    wsi_path: Path,
    mask_path: Path,
    cfg,
    mask_visualize_dir,
    tile_visualize_dir,
    num_workers: int = 4,
):
    """
    Process a single slide: extract tile coordinates and visualize if needed.
    """
    wsi_name = wsi_path.stem.replace(" ", "_")
    try:
        tissue_mask_visu_path = None
        if cfg.visualize and mask_visualize_dir is not None:
            tissue_mask_visu_path = Path(mask_visualize_dir, f"{wsi_name}.jpg")
        coordinates, tile_level, resize_factor, tile_size_lv0 = extract_coordinates(
            wsi_path=wsi_path,
            mask_path=mask_path,
            backend=cfg.tiling.backend,
            tiling_params=cfg.tiling.params,
            segment_params=cfg.tiling.seg_params,
            filter_params=cfg.tiling.filter_params,
            mask_visu_path=tissue_mask_visu_path,
            num_workers=num_workers,
        )
        coordinates_dir = Path(cfg.output_dir, "coordinates")
        coordinates_path = Path(coordinates_dir, f"{wsi_name}.npy")
        save_coordinates(
            coordinates=coordinates,
            target_spacing=cfg.tiling.params.spacing,
            tile_level=tile_level,
            tile_size=cfg.tiling.params.tile_size,
            resize_factor=resize_factor,
            tile_size_lv0=tile_size_lv0,
            save_path=coordinates_path,
        )
        if cfg.visualize and tile_visualize_dir is not None:
            visualize_coordinates(
                wsi_path=wsi_path,
                coordinates=coordinates,
                tile_size_lv0=tile_size_lv0,
                save_dir=tile_visualize_dir,
                downsample=cfg.tiling.visu_params.downsample,
                backend=cfg.tiling.backend,
            )
        return str(wsi_path), {"status": "success"}

    except Exception as e:
        return str(wsi_path), {
            "status": "failed",
            "error": str(e),
            "traceback": str(traceback.format_exc()),
        }


def main(args):
    # setup configuration
    cfg = get_cfg_from_file(args.config_file)
    output_dir = Path(cfg.output_dir, args.run_id)
    cfg.output_dir = str(output_dir)

    fix_random_seeds(cfg.seed)

    wsi_paths, mask_paths = load_csv(cfg)

    parallel_workers = min(mp.cpu_count(), cfg.speed.num_workers_tiling)
    if "SLURM_JOB_CPUS_PER_NODE" in os.environ:
        parallel_workers = min(
            parallel_workers, int(os.environ["SLURM_JOB_CPUS_PER_NODE"])
        )

    process_list = Path(cfg.output_dir, "process_list.csv")
    if process_list.is_file() and cfg.resume:
        process_df = pd.read_csv(process_list)
    else:
        data = {
            "wsi_name": [p.stem for p in wsi_paths],
            "wsi_path": [str(p) for p in wsi_paths],
            "mask_path": [str(p) if p is not None else p for p in mask_paths],
            "tiling_status": ["tbp"] * len(wsi_paths),
            "feature_status": ["tbp"] * len(wsi_paths),
            "error": [str(np.nan)] * len(wsi_paths),
            "traceback": [str(np.nan)] * len(wsi_paths),
        }
        if getattr(cfg.model, "level", None) == "slide":
            data["aggregation_status"] = ["tbp"] * len(wsi_paths)
        process_df = pd.DataFrame(data)

    skip_tiling = process_df["tiling_status"].str.contains("success").all()

    if not skip_tiling:
        if cfg.tiling.read_coordinates_from is not None:
            coordinates_dir = Path(cfg.tiling.read_coordinates_from)
            coordinates_files = list(coordinates_dir.glob("*.npy"))
            for coordinates_file in coordinates_files:
                wsi_name = coordinates_file.stem
                if wsi_name in process_df["wsi_name"].values:
                    process_df.loc[
                        process_df["wsi_name"] == wsi_name, "tiling_status"
                    ] = "success"
            process_df.to_csv(process_list, index=False)

        else:
            mask = process_df["tiling_status"] != "success"
            process_stack = process_df[mask]
            total = len(process_stack)

            wsi_paths_to_process = [
                Path(x) for x in process_stack.wsi_path.values.tolist()
            ]
            mask_paths_to_process = [
                Path(x) if x is not None else x
                for x in process_stack.mask_path.values.tolist()
            ]

            # setup directories for coordinates and visualization
            coordinates_dir = Path(cfg.output_dir, "coordinates")
            coordinates_dir.mkdir(exist_ok=True, parents=True)
            mask_visualize_dir = None
            tile_visualize_dir = None
            if cfg.visualize:
                visualize_dir = Path(cfg.output_dir, "visualization")
                mask_visualize_dir = Path(visualize_dir, "mask")
                tile_visualize_dir = Path(visualize_dir, "tiling")
                mask_visualize_dir.mkdir(exist_ok=True, parents=True)
                tile_visualize_dir.mkdir(exist_ok=True, parents=True)

            tiling_updates = {}
            with mp.Pool(processes=parallel_workers) as pool:
                args_list = [
                    {
                        "wsi_path": wsi_fp,
                        "mask_path": mask_fp,
                        "cfg": cfg,
                        "mask_visualize_dir": mask_visualize_dir,
                        "tile_visualize_dir": tile_visualize_dir,
                        "num_workers": parallel_workers,
                    }
                    for wsi_fp, mask_fp in zip(
                        wsi_paths_to_process, mask_paths_to_process
                    )
                ]
                results = list(
                    tqdm.tqdm(
                        pool.map(process_slide_wrapper, args_list),
                        total=total,
                        desc="Slide tiling",
                        unit="slide",
                        leave=True,
                    )
                )
            for wsi_path, status_info in results:
                tiling_updates[wsi_path] = status_info

            for wsi_path, status_info in tiling_updates.items():
                process_df.loc[
                    process_df["wsi_path"] == wsi_path, "tiling_status"
                ] = status_info["status"]
                if "error" in status_info:
                    process_df.loc[
                        process_df["wsi_path"] == wsi_path, "error"
                    ] = status_info["error"]
                    process_df.loc[
                        process_df["wsi_path"] == wsi_path, "traceback"
                    ] = status_info["traceback"]
            process_df.to_csv(process_list, index=False)

        # summary logging
        total_slides = len(process_df)
        slides_with_tiles = [
            str(p)
            for p in wsi_paths
            if Path(coordinates_dir, f"{p.stem}.npy").is_file()
        ]
        failed_tiling = process_df[process_df["tiling_status"] == "failed"]
        no_tiles = process_df[~process_df["wsi_path"].isin(slides_with_tiles)]
        print("=+=" * 10)
        print(f"Total number of slides: {total_slides}")
        print(f"Failed tiling: {len(failed_tiling)}")
        print(f"No tiles after tiling step: {len(no_tiles)}")
        print("=+=" * 10)

    else:
        print("=+=" * 10)
        print("All slides have been tiled. Skipping tiling step.")
        print("=+=" * 10)


if __name__ == "__main__":
    args = get_args_parser(add_help=True).parse_args()
    main(args)
