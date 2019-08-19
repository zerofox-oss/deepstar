import mock
import os
import unittest

from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir


class TestFrameSetSubDir(unittest.TestCase):
    """
    This class tests the FrameSetSubDir class.
    """

    def test_path(self):
        with mock.patch.dict(os.environ, {'DEEPSTAR_PATH': 'test'}):
            self.assertEqual(FrameSetSubDir.path(1), os.path.realpath('test/files/frame_sets/00000001'))  # noqa
