import mock
import os
import unittest

from deepstar.filesystem.video_dir import VideoDir

from .. import deepstar_path


class TestVideoDir(unittest.TestCase):
    """
    This class tests the VideoDir class.
    """

    def test_path(self):
        with mock.patch.dict(os.environ, {'DEEPSTAR_PATH': 'test'}):
            self.assertEqual(VideoDir.path(), os.path.realpath('test/files/videos'))  # noqa

    def test_init(self):
        with deepstar_path():
            VideoDir.init()
            self.assertTrue(os.path.isdir(VideoDir.path()))
