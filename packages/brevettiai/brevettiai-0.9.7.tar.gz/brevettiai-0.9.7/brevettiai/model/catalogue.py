from brevettiai.model.factory.mobilenetv2_backbone import lightning_segmentation_backbone, \
    thunder_segmentation_backbone, MobileNetV2SegmentationBackbone
from brevettiai.model.factory.lenet_backbone import lenet_backbone
from brevettiai.model.factory.lraspp import LRASPP2SegmentationHead, LRASPPSegmentationHead
from brevettiai.model.factory.unet import UnetSegmentationHead
from brevettiai.model.factory.segmentation import SegmentationModelFactory
from functools import partial
from typing import Literal, Optional
from pydantic import BaseModel, Field, root_validator


extended_backbone = partial(
    MobileNetV2SegmentationBackbone,
    output_layers=['block_1_expand_relu', 'block_6_expand_relu', 'block_13_expand_relu'],
    alpha=1
)

extended_backbone_full = partial(
    MobileNetV2SegmentationBackbone,
    output_layers=['input_2', 'block_1_expand_relu', 'block_6_expand_relu', 'block_13_expand_relu'],
    alpha=1
)

## input_2 if rgb else input_3
extended_backbone_full_unet = partial(
    MobileNetV2SegmentationBackbone,
    output_layers=["input_2", 'block_1_expand_relu', 'block_3_expand_relu', 'block_6_expand_relu', 'block_13_expand_relu', 'out_relu'],
    alpha=1
)

backbones = {
    "lightning": lightning_segmentation_backbone,
    "thunder": thunder_segmentation_backbone,
    "extended": extended_backbone,
    "full": extended_backbone_full,
    "full_unet": extended_backbone_full_unet,
    "lenet": lenet_backbone

}

heads = {
    "lraspp": LRASPPSegmentationHead,
    "lraspp2": LRASPP2SegmentationHead,
    "unet": UnetSegmentationHead
}


class SegmentationModelCatalogue(BaseModel):
    backbone_id: Literal[tuple(backbones.keys())]
    head_id: Literal[tuple(heads.keys())]
    bn_momentum: float = 0.9
    activation = "sigmoid"
    resize_method: Literal["bilinear", "nearest"] = "bilinear"
    resize_output: bool = False

    head_args: Optional[dict] = Field(default_factory=dict)
    backbone_args: Optional[dict] = Field(default_factory=dict)

    @root_validator(pre=True)
    def ids_are_always_lowercase(cls, values):
        values["backbone_id"] = values["backbone_id"].lower()
        values["head_id"] = values["head_id"].lower()
        return values

    def get_factory(self, classes):
        backbone_factory = backbones[self.backbone_id](**self.backbone_args)
        head_factory = heads[self.head_id](**self.head_args)
        factory = SegmentationModelFactory(
            backbone_factory=backbone_factory, head_factory=head_factory, classes=classes,
            bn_momentum=self.bn_momentum, activation=self.activation,
            resize_method=self.resize_method, resize_output=self.resize_output)
        return factory
