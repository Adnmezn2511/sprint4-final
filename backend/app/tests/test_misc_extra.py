import os
import zipfile
import tempfile
import unittest
from ..utils.misc import create_zip, delete_zip_file


class TestMiscExtra(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_zip_empty_folder(self):
        """Dossier vide → ZIP créé quand même."""
        empty = os.path.join(self.tmp.name, "empty")
        os.makedirs(empty)
        result = create_zip(empty, "empty_zip", self.tmp.name)
        self.assertTrue(os.path.exists(result))

    def test_create_zip_returns_path_ending_zip(self):
        src = os.path.join(self.tmp.name, "src")
        os.makedirs(src)
        result = create_zip(src, "myfile", self.tmp.name)
        self.assertTrue(result.endswith(".zip"))

    def test_delete_zip_returns_bool(self):
        """delete_zip_file retourne toujours un bool."""
        result = delete_zip_file(self.tmp.name, "nonexistent.zip")
        self.assertIsInstance(result, bool)

    def test_delete_zip_returns_false_missing(self):
        result = delete_zip_file(self.tmp.name, "ghost.zip")
        self.assertFalse(result)

    def test_create_then_delete_zip(self):
        src = os.path.join(self.tmp.name, "src2")
        os.makedirs(src)
        with open(os.path.join(src, "f.txt"), "w") as f:
            f.write("x")
        create_zip(src, "to_delete", self.tmp.name)
        result = delete_zip_file(self.tmp.name, "to_delete.zip")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()