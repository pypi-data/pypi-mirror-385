import unittest
import json

from brevettiai.tests.get_resources import get_resource
from brevettiai.data.image.modules import AnnotationLoader
from brevettiai.data.tf_types import BBOX
from brevettiai.io import io_tools
from brevettiai.platform import ImageAnnotation


class TestPlatformAnnotation(unittest.TestCase):
    test_annotation_path = get_resource("1651574629796.json")
    bbox = BBOX(x1=10, x2=210, y1=30, y2=130)

    def test_annotation_from_segmentation(self):
        classes = set([anno["label"] for anno in
                       json.loads(io_tools.read_file(self.test_annotation_path))["annotations"]])
        annotation_bbox, _ = AnnotationLoader(classes=classes).load(path=self.test_annotation_path, bbox=self.bbox)

        image_annotation = ImageAnnotation.from_segmentation(annotation_bbox,
                                                             classes=classes, sample=dict(),
                                                             image_shape=annotation_bbox.shape,
                                                             get_features=["polygon", "segmentation"])
        df = image_annotation.to_dataframe()
        assert len(df.label.unique()) == 3


if __name__ == '__main__':
    unittest.main()
