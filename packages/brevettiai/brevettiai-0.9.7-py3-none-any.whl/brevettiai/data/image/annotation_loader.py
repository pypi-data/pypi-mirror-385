import tensorflow as tf
from pydantic import Field, PrivateAttr, validator
from pydantic.typing import Literal
from typing import Dict, Optional, List, ClassVar, Type
from brevettiai.data.data_generator import FileLoader
import json
import numpy as np
from brevettiai.data.image import annotation_parser, ImageKeys
from brevettiai.data.image.image_loader import CropResizeProcessor
from brevettiai.data.tf_types import BBOX


class AnnotationLoader(FileLoader):
    type: Literal["AnnotationLoader"] = "AnnotationLoader"

    mini_contour_max_area: int = Field(
        default=0,
        description="max area for contours to get their border drawn as well as their filling")
    mini_contour_line_thickness: int = Field(
        default=0,
        description="Line thickness to apply when drawing contours smaller than 'mini_contout_max_area")

    path_key: str = Field(default="annotation_path", exclude=True)
    output_key: str = Field(default="annotation", exclude=True)
    bbox_meta: ClassVar[Type] = BBOX
    metadata_spec = {
        "_image_file_shape": None,
        ImageKeys.BOUNDING_BOX: BBOX.build,
        ImageKeys.ZOOM: int,
    }
    mapping: Dict[str, str] = Field(default_factory=dict,
                                    description="mapping from annotation label to class, use '|' to signal multiclass")

    classes: List[str] = Field(default=None, exclude=True)
    postprocessor: Optional[CropResizeProcessor] = Field(default_factory=None, exclude=True)

    _label_space = PrivateAttr(default=None)

    @validator('mapping', each_item=True, pre=True, allow_reuse=True)
    def convert_non_str_to_pipe_separated_string(cls, v):
        if not isinstance(v, str):
            return "|".join(v)
        return v

    @property
    def label_space(self):
        assert self.classes is not None
        if self._label_space is not None:
            return self._label_space

        self._label_space = {}
        targets = dict(zip(self.classes, np.eye(len(self.classes))))
        self._label_space.update(targets)
        for label, class_descriptor in self.mapping.items():
            # Separate multiclass to classes
            classes = [x for x in class_descriptor.split("|") if x in self.classes]
            # map classes to
            if classes:
                self._label_space[label] = np.max(tuple(targets[c] for c in classes), 0)
        return self._label_space

    def load(self, path, metadata: dict = None, postprocess: bool = True, zoom: int = 1, bbox: BBOX = BBOX()):
        metadata = metadata or dict()
        zoom = metadata.get(ImageKeys.ZOOM, zoom)
        bbox = metadata.get(ImageKeys.BOUNDING_BOX, bbox)
        bbox_shape = bbox.shape
        shape = metadata.get("_image_file_shape", bbox_shape)[:2]
        shape = tf.where(tf.convert_to_tensor(bbox_shape) > 1, bbox_shape, shape)

        data, meta = super().load(path, metadata)
        label_space = self.label_space
        if postprocess and self.postprocessor is not None:
            sy, sx = self.postprocessor.scale(shape[0], shape[1])
            scale_ = (1/(sy*zoom), 1/(sx*zoom))
            offset = (-self.postprocessor.roi_vertical_offset, -self.postprocessor.roi_horizontal_offset)
            shape = self.postprocessor.output_size(shape[0], shape[1])
        else:
            offset = (0, 0)
            scale_ = (1/zoom, 1/zoom)

        def _parse_annotation_buffer(buffer, shape, scale, bbox):
            draw_buffer = np.zeros((shape[2], shape[0], shape[1]), dtype=np.float32)
            try:
                # Decode if bytes
                buffer = buffer.decode()
            except AttributeError:
                # take item if numpy array
                buffer = buffer.item()
            if len(buffer) > 0:
                annotation = json.loads(buffer)
                offset_dynamic = (offset - bbox[:2])
                segmentation = annotation_parser.draw_contours2_CHW(
                    annotation, label_space,
                    scale=scale[::-1], draw_buffer=draw_buffer,
                    offset=offset_dynamic[::-1],
                    mini_contour_max_area=self.mini_contour_max_area,
                    mini_contour_line_thickness=self.mini_contour_line_thickness)
            else:
                segmentation = draw_buffer
            segmentation = segmentation.transpose(1, 2, 0)
            return segmentation.astype(np.float32)

        annotation = tf.numpy_function(_parse_annotation_buffer,
                                       [data, (shape[0], shape[1], len(self.classes)), scale_, tuple(bbox)],
                                       tf.float32, name="parse_segmentation")
        annotation = tf.ensure_shape(annotation, (shape[0], shape[1], len(self.classes)))

        meta = {}
        return annotation, meta