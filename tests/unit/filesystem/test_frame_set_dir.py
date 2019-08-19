import mock
import os
import unittest

from deepstar.filesystem.frame_set_dir import FrameSetDir

from .. import deepstar_path


class TestFrameSetDir(unittest.TestCase):
    """
    This class tests the FrameSetDir class.
    """

    def test_path(self):
        with mock.patch.dict(os.environ, {'DEEPSTAR_PATH': 'test'}):
            self.assertEqual(FrameSetDir.path(), os.path.realpath('test/files/frame_sets'))  # noqa

    def test_init(self):
        with deepstar_path():
            FrameSetDir.init()
            self.assertTrue(os.path.isdir(FrameSetDir.path()))
