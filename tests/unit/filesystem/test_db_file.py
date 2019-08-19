import mock
import os
import unittest

from deepstar.filesystem.db_file import DBFile


class TestDBFile(unittest.TestCase):
    """
    This class tests the DBFile class.
    """

    def test_path(self):
        with mock.patch.dict(os.environ, {'DEEPSTAR_PATH': 'test'}):
            self.assertEqual(DBFile.path(), os.path.realpath('test/db/deepstar.sqlite3'))  # noqa
