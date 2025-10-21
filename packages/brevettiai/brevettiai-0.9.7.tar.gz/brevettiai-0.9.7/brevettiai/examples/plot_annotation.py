from brevettiai.platform import PlatformAPI
from brevettiai.tooling import plot
from brevettiai.tests.test_annotation_tooling import TestAnnotationTooling


def find_annotation():
    web = PlatformAPI()
    web.get_dataset()
    return


def main():
    annotation = TestAnnotationTooling.build_test_annotation()
    plot.imshow(TestAnnotationTooling.test_image, cmap="gray")
    plot.annotation(annotation)
    plot.show()


if __name__ == "__main__":
    main()
