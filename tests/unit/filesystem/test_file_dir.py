import mock
import os
import unittest

from deepstar.filesystem.file_dir import FileDir

from .. import deepstar_path


class TestFileDir(unittest.TestCase):
    """
    This class tests the FileDir class.
    """

    def test_path(self):
        with mock.patch.dict(os.environ, {'DEEPSTAR_PATH': 'test'}):
            self.assertEqual(FileDir.path(), os.path.realpath('test/files'))

    def test_init(self):
        with deepstar_path():
            FileDir.init()
            self.assertTrue(os.path.isdir(FileDir.path()))
