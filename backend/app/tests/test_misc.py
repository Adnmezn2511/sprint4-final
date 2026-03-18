import os
import zipfile
import tempfile
import unittest
from app.utils.misc import create_zip, delete_zip_file


class TestCreateZip(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.source = os.path.join(self.tmp.name, "source")
        os.makedirs(self.source)
        with open(os.path.join(self.source, "file1.txt"), "w") as f:
            f.write("hello")
        with open(os.path.join(self.source, "file2.txt"), "w") as f:
            f.write("world")
        self.output_dir = os.path.join(self.tmp.name, "output")

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_zip_file(self):
        result = create_zip(self.source, "myzip", self.output_dir)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".zip"))

    def test_zip_contains_files(self):
        create_zip(self.source, "myzip", self.output_dir)
        zip_path = os.path.join(self.output_dir, "myzip.zip")
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
        self.assertIn("file1.txt", names)
        self.assertIn("file2.txt", names)

    def test_output_dir_created_if_missing(self):
        new_dir = os.path.join(self.tmp.name, "new_output")
        self.assertFalse(os.path.exists(new_dir))
        create_zip(self.source, "myzip", new_dir)
        self.assertTrue(os.path.exists(new_dir))

    def test_returns_correct_path(self):
        result = create_zip(self.source, "myzip", self.output_dir)
        expected = os.path.join(self.output_dir, "myzip.zip")
        self.assertEqual(result, expected)

    def test_zip_subdirectory(self):
        subdir = os.path.join(self.source, "sub")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "deep.txt"), "w") as f:
            f.write("deep")
        create_zip(self.source, "myzip", self.output_dir)
        zip_path = os.path.join(self.output_dir, "myzip.zip")
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
        self.assertTrue(any("deep.txt" in n for n in names))


class TestDeleteZipFile(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_delete_existing_zip(self):
        zip_path = os.path.join(self.tmp.name, "test.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("a.txt", "data")
        result = delete_zip_file(self.tmp.name, "test.zip")
        self.assertTrue(result)
        self.assertFalse(os.path.exists(zip_path))

    def test_delete_adds_extension_if_missing(self):
        zip_path = os.path.join(self.tmp.name, "test.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("a.txt", "data")
        result = delete_zip_file(self.tmp.name, "test")
        self.assertTrue(result)
        self.assertFalse(os.path.exists(zip_path))

    def test_delete_nonexistent_returns_false(self):
        result = delete_zip_file(self.tmp.name, "nonexistent.zip")
        self.assertFalse(result)

    def test_delete_wrong_dir_returns_false(self):
        result = delete_zip_file("/nonexistent/path", "file.zip")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()