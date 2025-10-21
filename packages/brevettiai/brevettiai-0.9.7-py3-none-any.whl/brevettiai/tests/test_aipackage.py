import json
import os
import random
import string
import unittest
from tempfile import TemporaryDirectory

from brevettiai.platform import AIPackage
from brevettiai.tests.test_model_metadata import TestModelMetadata


class TestAIPackage(unittest.TestCase):
    def test_write_archive(self):
        with TemporaryDirectory() as tmpdir:
            asset_name = "test"
            asset_content = b'test'
            testfile = os.path.join(tmpdir, "test.txt")
            testpackage = os.path.join(tmpdir, "test.aipkg")

            with open(testfile, "wb") as fp:
                fp.write(asset_content)

            meta = json.loads(TestModelMetadata.image_segmentation_metadata[0])
            pw = ''.join(random.choice(string.printable) for _ in range(10))
            archive = AIPackage(path=testpackage, metadata=meta, password=pw)

            # Test file not found
            self.assertRaises(FileNotFoundError, archive.open_read)

            # Write package
            with archive.open_write() as writer:
                self.assertRaises(IOError, archive.open_read)
                writer.add_asset(asset_name, "test.txt", testfile)

            # Check versioned name
            self.assertRegex(archive.versioned_name, r"test\.\d+\.aipkg")

            # Load package without password
            self.assertRaises(OSError, AIPackage, path=testpackage)

            # Load package with password
            archive_out = AIPackage(path=testpackage, password=pw)
            with archive_out.open_read() as reader:
                self.assertRaises(IOError, archive_out.open_write)
                data = reader.get_asset(asset_name)
                self.assertEqual(data.read(), asset_content)


if __name__ == '__main__':
    unittest.main()
