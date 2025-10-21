import unittest
import os
from brevettiai.datamodel import ImageAnnotation
from brevettiai.tooling.annotation_tools import extract_annotations
import numpy as np


class TestAnnotationTooling(unittest.TestCase):
    test_image_annotation = """
    {
      "annotations": [
        {
          "label": "Defect",
          "color": "#ff0000",
          "type": "point",
          "points": [
            {
              "x": 461.21825004774934,
              "y": 327.7686642831313
            }
          ],
          "severity": null,
          "visibility": null
        },
        {
          "label": "Defect",
          "color": "#ff0001",
          "type": "rectangle",
          "points": [
            {
              "x": 461.21825004774934,
              "y": 327.7686642831313
            },
            {
              "x": 458.3382500477494,
              "y": 334.0086642831312
            }
          ],
          "severity": null,
          "visibility": null
        },
        {
          "label": "Defect",
          "color": "#ff0002",
          "type": "line",
          "points": [
            {
              "x": 461.21825004774934,
              "y": 327.7686642831313
            },
            {
              "x": 458.3382500477494,
              "y": 334.0086642831312
            }
          ],
          "severity": null,
          "visibility": null
        },
        {
          "label": "Container",
          "color": "#ff0003",
          "type": "polygon",
          "points": [
            {
              "x": 302.48520710059177,
              "y": 109.51923076923077
            },
            {
              "x": 277.86982248520707,
              "y": 111.41272189349112
            },
            {
              "x": 237.6331360946746,
              "y": 120.8801775147929
            },
            {
              "x": 193.02752293577907,
              "y": 143.9946483180426
            },
            {
              "x": 165.5045871559626,
              "y": 172.74082568807316
            },
            {
              "x": 141.65137614678827,
              "y": 214.33103975535147
            },
            {
              "x": 129.41896024464756,
              "y": 260.202599388379
            },
            {
              "x": 130.64220183486162,
              "y": 304.23929663608544
            },
            {
              "x": 141.65137614678827,
              "y": 340.93654434250743
            },
            {
              "x": 160.61162079510626,
              "y": 374.57568807339436
            },
            {
              "x": 185.07645259938766,
              "y": 403.93348623853194
            },
            {
              "x": 216.26911314984636,
              "y": 425.3402140672781
            },
            {
              "x": 257.5935922781142,
              "y": 440.1037018145247
            },
            {
              "x": 299.6739839167797,
              "y": 443.24989932021936
            },
            {
              "x": 346.4736718139872,
              "y": 436.17095493240646
            },
            {
              "x": 383.0482178176871,
              "y": 418.4735939628743
            },
            {
              "x": 412.5438194335742,
              "y": 394.87711267016465
            },
            {
              "x": 435.3537513498601,
              "y": 364.98823636606573
            },
            {
              "x": 449.9049148136977,
              "y": 335.8859094383905
            },
            {
              "x": 458.95023264256974,
              "y": 300.8844621875379
            },
            {
              "x": 461.7031554600526,
              "y": 264.30991618383797
            },
            {
              "x": 454.78586084989496,
              "y": 221.12507620013716
            },
            {
              "x": 439.05487332142184,
              "y": 186.51690363749637
            },
            {
              "x": 415.8079768669269,
              "y": 156.49686754500266
            },
            {
              "x": 385.8079768669269,
              "y": 133.49686754500266
            },
            {
              "x": 358.14131020026025,
              "y": 118.83020087833599
            },
            {
              "x": 330.41420118343194,
              "y": 111.41272189349112
            }
          ],
          "severity": null,
          "visibility": null
        }
      ],
      "image": {
        "fileName": "Defect FlipOff/TV12/IMG_2022_11_11_14_35_19_958_camA_000.png",
        "width": 640,
        "height": 480
      }
    }
    """
    test_image = np.array([
        [1,0,0,0,0,0,1],
        [0,0,1,1,1,0,0],
        [0,1,0,0,0,1,0],
        [0,1,0,1,0,1,0],
        [0,1,0,0,0,1,0],
        [0,0,1,1,1,0,0],
        [1,0,0,0,0,0,1],
        [1,0,1,1,0,0,1],
        [1,0,0,0,0,0,1],
        [1,0,0,0,0,1,0],
        [1,0,0,0,0,1,0],
        [1,0,0,0,1,0,0],
        [1,0,0,0,1,0,0],
        [1,0,0,0,1,0,0],
        [1,0,0,1,0,0,0],
        [1,0,0,1,0,0,0],
        [1,0,0,1,0,0,0],
        [1,0,0,1,1,0,1],
        [1,0,0,0,1,1,1],
    ])

    @classmethod
    def build_test_annotation(cls) -> ImageAnnotation:
        extract_args = dict(min_area=0)
        return extract_annotations(cls.test_image, classes=["A"], threshold=0.5, extract_args=extract_args)

    def test_parse_annotaion(self):
        annotation = ImageAnnotation.parse_raw(self.test_image_annotation)

    def test_parse_contour(self):
        self.build_test_annotation()

    @unittest.skipIf(os.getenv("CI", ""), "UI test")
    def test_plt_contour(self):
        from brevettiai.tooling import plot

        img_ann = self.build_test_annotation()

        plot.imshow(self.test_image, cmap="gray")
        plot.annotation(img_ann)
        plot.show()


if __name__ == '__main__':
    unittest.main()
