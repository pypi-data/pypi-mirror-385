import unittest
import tensorflow as tf

from brevettiai.model.catalogue import SegmentationModelCatalogue


class TestModelCatalogue(unittest.TestCase):
    def test_model_factory(self):
        factory = SegmentationModelCatalogue(
            resize_output=True,
            backbone_id="lightning",
            head_id="LRASPP2"
        ).get_factory(classes=["dummy1", "dummy2"])
        segmentation_model = factory.build(input_shape=(None, None, 3))
        assert(isinstance(segmentation_model, tf.keras.models.Model))


if __name__ == '__main__':
    unittest.main()

