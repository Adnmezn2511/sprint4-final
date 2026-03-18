import os
import unittest
from ..multixrank.PathManager import PathManager


class TestPathManager(unittest.TestCase):

    def test_get_package_path_returns_string(self):
        path = PathManager.get_package_path()
        self.assertIsInstance(path, str)

    def test_get_package_path_exists(self):
        path = PathManager.get_package_path()
        self.assertTrue(os.path.exists(path))

    def test_get_package_path_is_directory(self):
        path = PathManager.get_package_path()
        self.assertTrue(os.path.isdir(path))

    def test_get_package_path_consistent(self):
        """Appels successifs retournent le même chemin."""
        path1 = PathManager.get_package_path()
        path2 = PathManager.get_package_path()
        self.assertEqual(path1, path2)


if __name__ == "__main__":
    unittest.main()