import timm
import torch
import logging
import torch.nn as nn

from einops import rearrange
from omegaconf import DictConfig
from transformers import AutoModel
from torchvision import transforms
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform

import slide2vec.distributed as distributed
import slide2vec.models.vision_transformer_dino as vits_dino
import slide2vec.models.vision_transformer_dinov2 as vits_dinov2

from slide2vec.utils import update_state_dict
from slide2vec.data.augmentations import make_normalize_transform, MaybeToTensor

logger = logging.getLogger("slide2vec")


class ModelFactory:
    def __init__(
        self,
        options: DictConfig,
    ):
        if options.level == "tile":
            if options.name == "virchow":
                model = Virchow(mode=options.mode)
            elif options.name == "virchow2":
                model = Virchow2(mode=options.mode)
            elif options.name == "uni":
                model = UNI()
            elif options.name == "uni2":
                model = UNI2()
            elif options.name == "prov-gigapath":
                model = ProvGigaPath()
            elif options.name == "h-optimus-0":
                model = Hoptimus0()
            elif options.name == "h-optimus-1":
                model = Hoptimus1()
            elif options.name == "h-optimus-0-mini" or options.name == "h0-mini":
                model = Hoptimus0Mini(
                    mode=options.mode
                )
            elif options.name == "rumc-vit-s-50k":
                model = CustomViT(
                    arch=options.arch,
                    pretrained_weights=options.pretrained_weights,
                    num_register_tokens=0,
                )
            elif options.name is None and options.arch:
                model = DINOViT(
                    arch=options.arch,
                    pretrained_weights=options.pretrained_weights,
                    input_size=options.tile_size,
                )
        elif options.level == "region":
            if options.name == "virchow":
                tile_encoder = Virchow()
            elif options.name == "virchow2":
                tile_encoder = Virchow2()
            elif options.name == "uni":
                tile_encoder = UNI()
            elif options.name == "uni2":
                tile_encoder = UNI2()
            elif options.name == "prov-gigapath":
                tile_encoder = ProvGigaPath()
            elif options.name == "h-optimus-0":
                tile_encoder = Hoptimus0()
            elif options.name == "h-optimus-1":
                tile_encoder = Hoptimus1()
            elif options.name == "rumc-vit-s-50k":
                tile_encoder = CustomViT(
                    arch=options.arch,
                    pretrained_weights=options.pretrained_weights,
                    num_register_tokens=0,
                )
            elif options.name is None and options.arch:
                tile_encoder = DINOViT(
                    arch=options.arch,
                    pretrained_weights=options.pretrained_weights,
                    input_size=options.patch_size,
                )
            model = RegionFeatureExtractor(tile_encoder)
        elif options.level == "slide":
            if options.name == "prov-gigapath":
                model = ProvGigaPathSlide()
            elif options.name == "titan":
                model = TITAN()
            elif options.name == "prism":
                model = PRISM()
            else:
                raise ValueError(f"{options.name} doesn't support slide-level encoding")

        self.model = model.eval()
        self.model = self.model.to(self.model.device)

    def get_model(self):
        return self.model


class FeatureExtractor(nn.Module):
    def __init__(self):
        super(FeatureExtractor, self).__init__()
        self.encoder = self.build_encoder()
        self.set_device()

    def set_device(self):
        if distributed.is_enabled():
            self.device = torch.device(f"cuda:{distributed.get_local_rank()}")
        else:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")

    def build_encoder(self):
        raise NotImplementedError

    def get_transforms(self):
        data_config = resolve_data_config(
            self.encoder.pretrained_cfg, model=self.encoder
        )
        transform = create_transform(**data_config)
        return transform

    def forward(self, x):
        raise NotImplementedError


class DINOViT(FeatureExtractor):
    def __init__(
        self,
        arch: str,
        pretrained_weights: str,
        input_size: int = 256,
        patch_size: int = 14,
        ckpt_key: str = "teacher",
    ):
        self.arch = arch
        self.pretrained_weights = pretrained_weights
        self.input_size = input_size
        self.patch_size = patch_size
        self.ckpt_key = ckpt_key
        arch2dim = {"vit_large": 1024, "vit_base": 768, "vit_small": 384}
        self.features_dim = arch2dim[arch]
        super(DINOViT, self).__init__()
        self.load_weights()

    def load_weights(self):
        if distributed.is_main_process():
            print(f"Loading pretrained weights from: {self.pretrained_weights}")
        state_dict = torch.load(self.pretrained_weights, map_location="cpu")
        if self.ckpt_key:
            state_dict = state_dict[self.ckpt_key]
        nn.modules.utils.consume_prefix_in_state_dict_if_present(
            state_dict, prefix="module."
        )
        nn.modules.utils.consume_prefix_in_state_dict_if_present(
            state_dict, prefix="backbone."
        )
        state_dict, msg = update_state_dict(model_dict=self.encoder.state_dict(), state_dict=state_dict)
        if distributed.is_main_process():
            print(msg)
        self.encoder.load_state_dict(state_dict, strict=False)

    def build_encoder(self):
        encoder = vits_dino.__dict__[self.arch](
            img_size=self.input_size, patch_size=self.patch_size
        )
        return encoder

    def get_transforms(self):
        if self.input_size > 224:
            transform = transforms.Compose(
                [
                    MaybeToTensor(),
                    transforms.CenterCrop(224),
                    make_normalize_transform(),
                ]
            )
        else:
            transforms.Compose(
                [
                    MaybeToTensor(),
                    make_normalize_transform(),
                ]
            )
        return transform

    def forward(self, x):
        return self.encoder(x)


class CustomViT(FeatureExtractor):
    def __init__(
        self,
        arch: str,
        pretrained_weights: str,
        num_register_tokens: int = 0,
        ckpt_key: str = "teacher",
    ):
        """_summary_

        Args:
            arch (str): architecture of the Vision Transformer model
            pretrained_weights (str): path to the pretrained weights
            ckpt_key (str, optional): checkpoint key to load the weights. Defaults to "teacher".
        """
        self.arch = arch
        self.pretrained_weights = pretrained_weights
        self.vit_kwargs = dict(
            img_size=224,
            patch_size=14,
            init_values=1.0e-05,
            ffn_layer="swiglufused",
            block_chunks=4,
            qkv_bias=True,
            proj_bias=True,
            ffn_bias=True,
            num_register_tokens=num_register_tokens,
            interpolate_offset=0.1,
            interpolate_antialias=False,
        )
        self.ckpt_key = ckpt_key
        arch2dim = {"vit_large": 1024, "vit_base": 768, "vit_small": 384}
        self.features_dim = arch2dim[arch]
        super(CustomViT, self).__init__()
        self.load_weights()

    def load_weights(self):
        if distributed.is_main_process():
            print(f"Loading pretrained weights from: {self.pretrained_weights}")
        state_dict = torch.load(self.pretrained_weights, map_location="cpu")
        if self.ckpt_key:
            state_dict = state_dict[self.ckpt_key]
        nn.modules.utils.consume_prefix_in_state_dict_if_present(
            state_dict, prefix="module."
        )
        nn.modules.utils.consume_prefix_in_state_dict_if_present(
            state_dict, prefix="backbone."
        )
        state_dict, msg = update_state_dict(model_dict=self.encoder.state_dict(), state_dict=state_dict)
        if distributed.is_main_process():
            print(msg)
        self.encoder.load_state_dict(state_dict, strict=False)

    def build_encoder(self):
        encoder = vits_dinov2.__dict__[self.arch](**self.vit_kwargs)
        return encoder

    def get_transforms(self):
        transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Resize(224),
                transforms.CenterCrop(224),
                make_normalize_transform(),
            ]
        )
        return transform

    def forward(self, x):
        return self.encoder(x)


class UNI(FeatureExtractor):
    def __init__(self):
        self.features_dim = 1024
        super(UNI, self).__init__()

    def build_encoder(self):
        encoder = timm.create_model(
            "hf-hub:MahmoodLab/UNI",
            pretrained=True,
            init_values=1e-5,
            dynamic_img_size=True,
        )
        return encoder

    def forward(self, x):
        return self.encoder(x)


class UNI2(FeatureExtractor):
    def __init__(self):
        self.features_dim = 1536
        super(UNI2, self).__init__()

    def build_encoder(self):
        timm_kwargs = {
            "img_size": 224,
            "patch_size": 14,
            "depth": 24,
            "num_heads": 24,
            "init_values": 1e-5,
            "embed_dim": 1536,
            "mlp_ratio": 2.66667 * 2,
            "num_classes": 0,
            "no_embed_class": True,
            "mlp_layer": timm.layers.SwiGLUPacked,
            "act_layer": torch.nn.SiLU,
            "reg_tokens": 8,
            "dynamic_img_size": True,
        }
        encoder = timm.create_model(
            "hf-hub:MahmoodLab/UNI2-h", pretrained=True, **timm_kwargs
        )
        return encoder

    def forward(self, x):
        return self.encoder(x)


class Virchow(FeatureExtractor):
    def __init__(self, mode: str = "cls"):
        self.mode = mode
        self.features_dim = 1280
        if mode == "full":
            self.features_dim = 2560
        super(Virchow, self).__init__()

    def build_encoder(self):
        encoder = timm.create_model(
            "hf-hub:paige-ai/Virchow",
            pretrained=True,
            mlp_layer=timm.layers.SwiGLUPacked,
            act_layer=torch.nn.SiLU,
        )
        return encoder

    def forward(self, x):
        output = self.encoder(x)
        class_token = output[:, 0]  # size: 1 x 1280
        patch_tokens = output[
            :, 1:
        ]  # size: 1 x 256 x 1280, tokens 1-4 are register tokens so we ignore those
        if self.mode == "cls":
            return class_token
        elif self.mode == "full":
            embedding = torch.cat(
                [class_token, patch_tokens.mean(1)], dim=-1
            )  # size: 1 x 2560
            return embedding


class Virchow2(FeatureExtractor):
    def __init__(self, mode: str = "cls"):
        self.mode = mode
        self.features_dim = 1280
        if mode == "full":
            self.features_dim = 2560
        super(Virchow2, self).__init__()

    def build_encoder(self):
        encoder = timm.create_model(
            "hf-hub:paige-ai/Virchow2",
            pretrained=True,
            mlp_layer=timm.layers.SwiGLUPacked,
            act_layer=torch.nn.SiLU,
        )
        return encoder

    def forward(self, x):
        output = self.encoder(x)
        class_token = output[:, 0]  # size: 1 x 1280
        patch_tokens = output[
            :, 5:
        ]  # size: 1 x 256 x 1280, tokens 1-4 are register tokens so we ignore those
        if self.mode == "cls":
            return class_token
        elif self.mode == "full":
            embedding = torch.cat(
                [class_token, patch_tokens.mean(1)], dim=-1
            )  # size: 1 x 2560
            return embedding


class ProvGigaPath(FeatureExtractor):
    def __init__(self):
        self.features_dim = 1536
        super(ProvGigaPath, self).__init__()

    def build_encoder(self):
        encoder = timm.create_model(
            "hf_hub:prov-gigapath/prov-gigapath",
            pretrained=True,
        )
        return encoder

    def forward(self, x):
        return self.encoder(x)


class Hoptimus0(FeatureExtractor):
    def __init__(self):
        self.features_dim = 1536
        super(Hoptimus0, self).__init__()

    def build_encoder(self):
        encoder = timm.create_model(
            "hf-hub:bioptimus/H-optimus-0",
            pretrained=True,
            init_values=1e-5,
            dynamic_img_size=False,
        )
        return encoder

    def forward(self, x):
        return self.encoder(x)


class Hoptimus1(FeatureExtractor):
    def __init__(self):
        self.features_dim = 1536
        super(Hoptimus1, self).__init__()

    def build_encoder(self):
        encoder = timm.create_model(
            "hf-hub:bioptimus/H-optimus-1",
            pretrained=True,
            init_values=1e-5,
            dynamic_img_size=False,
        )
        return encoder

    def forward(self, x):
        return self.encoder(x)


class Hoptimus0Mini(FeatureExtractor):
    def __init__(self, mode: str = "cls"):
        self.mode = mode
        self.features_dim = 768
        if mode == "full":
            self.features_dim = 1536
        super(Hoptimus0Mini, self).__init__()

    def build_encoder(self):
        encoder = timm.create_model(
            "hf-hub:bioptimus/H0-mini",
            pretrained=True,
            mlp_layer=timm.layers.SwiGLUPacked,
            act_layer=torch.nn.SiLU,
        )
        return encoder

    def forward(self, x):
        output = self.encoder(x)
        cls_features = output[:, 0]  # size: 1 x 768
        patch_token_features = output[
            :, self.encoder.num_prefix_tokens :
        ]  # size: 1 x 256 x 768
        if self.mode == "cls":
            return cls_features
        elif self.mode == "full":
            embedding = torch.cat(
                [cls_features, patch_token_features.mean(1)], dim=-1
            )  # size: 1 x 1536
            return embedding


class RegionFeatureExtractor(nn.Module):
    def __init__(
        self,
        tile_encoder: nn.Module,
        tile_size: int = 256,
    ):
        super(RegionFeatureExtractor, self).__init__()
        self.tile_encoder = tile_encoder
        self.tile_size = tile_size
        self.device = self.tile_encoder.device
        self.features_dim = self.tile_encoder.features_dim

    def get_transforms(self):
        return self.tile_encoder.get_transforms()

    def forward(self, x):
        # x = [B, num_tiles, 3, 224, 224]
        B = x.size(0)
        x = rearrange(x, "b p c w h -> (b p) c w h")  # [B*num_tiles, 3, 224, 224]
        output = self.tile_encoder(x)  # [B*num_tiles, features_dim]
        output = rearrange(
            output, "(b p) f -> b p f", b=B
        )  # [B, num_tiles, features_dim]
        return output


class SlideFeatureExtractor(nn.Module):
    def __init__(self):
        super(SlideFeatureExtractor, self).__init__()
        self.build_encoders()
        self.set_device()
        self.features_dim = None

    def build_encoders(self):
        raise NotImplementedError

    def set_device(self):
        if distributed.is_enabled():
            self.device = torch.device(f"cuda:{distributed.get_local_rank()}")
        else:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")

    def get_transforms(self):
        return self.tile_encoder.get_transforms()

    def forward(self, x):
        return self.tile_encoder(x)

    def forward_slide(self, **kwargs):
        return self.slide_encoder(**kwargs)


class ProvGigaPathSlide(SlideFeatureExtractor):
    def __init__(
        self,
    ):
        super(ProvGigaPathSlide, self).__init__()
        self.features_dim = self.tile_encoder.features_dim

    def build_encoders(self):
        import gigapath.slide_encoder as sd

        self.tile_encoder = ProvGigaPath()
        self.slide_encoder = sd.create_model(
            "hf_hub:prov-gigapath/prov-gigapath",
            "gigapath_slide_enc12l768d",
            self.tile_encoder.features_dim,
        )

    def forward_slide(self, tile_features, tile_coordinates, **kwargs):
        tile_features = tile_features.unsqueeze(0)
        output = self.slide_encoder(tile_features, tile_coordinates)
        output = output[0].squeeze()
        return output


class TITAN(SlideFeatureExtractor):
    def __init__(self):
        super(TITAN, self).__init__()
        self.features_dim = 768

    def build_encoders(self):
        self.slide_encoder = AutoModel.from_pretrained(
            "MahmoodLab/TITAN", trust_remote_code=True
        )
        self.tile_encoder, self.eval_transform = self.slide_encoder.return_conch()

    def get_transforms(self):
        return self.eval_transform

    def forward_slide(self, tile_features, tile_coordinates, tile_size_lv0, **kwargs):
        tile_features = tile_features.unsqueeze(0)
        tile_coordinates = tile_coordinates.unsqueeze(0)
        output = self.slide_encoder.encode_slide_from_patch_features(
            tile_features, tile_coordinates, tile_size_lv0
        )
        return output


class PRISM(SlideFeatureExtractor):
    def __init__(self):
        super(PRISM, self).__init__()
        self.features_dim = self.tile_encoder.features_dim

    def build_encoders(self):
        self.slide_encoder = AutoModel.from_pretrained(
            "paige-ai/PRISM", trust_remote_code=True
        )
        self.tile_encoder = Virchow(mode="full")

    def forward_slide(self, tile_features, **kwargs):
        tile_features = tile_features.unsqueeze(0)
        reprs = self.slide_encoder.slide_representations(tile_features)
        output = reprs["image_embedding"].squeeze(0)  # [1280]
        return output
