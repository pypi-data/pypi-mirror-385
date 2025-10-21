# Take care what you put in here. It will be loaded by all users of the library

from .camelmodel import CamelModel
from .dataset import Dataset, DatasetItem, DatasetItemMetadata, DatasetObject
from .image_annotation import ImageAnnotation, AnnotationTypes, PolygonAnnotation,\
    RectangleAnnotation, LineAnnotation, PointAnnotation
from .tag import Tag
from .image import BBOX, SequenceShape, ImageRegion, SequenceRange
