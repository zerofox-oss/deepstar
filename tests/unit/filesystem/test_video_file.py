import mock
import os
import unittest

from deepstar.filesystem.video_file import VideoFile


class TestVideoFile(unittest.TestCase):
    """
    This class tests the VideoFile class.
    """

    def test_path(self):
        with mock.patch.dict(os.environ, {'DEEPSTAR_PATH': 'test'}):
            self.assertEqual(VideoFile.path('test'), os.path.realpath('test/files/videos/test'))  # noqa
