import mock
import os
import unittest

from deepstar.filesystem.db_dir import DBDir

from .. import deepstar_path


class TestDBDir(unittest.TestCase):
    """
    This class tests the DBDir class.
    """

    def test_path(self):
        with mock.patch.dict(os.environ, {'DEEPSTAR_PATH': 'test'}):
            self.assertEqual(DBDir.path(), os.path.realpath('test/db'))

    def test_init(self):
        with deepstar_path():
            DBDir.init()
            self.assertTrue(os.path.isdir(DBDir.path()))
