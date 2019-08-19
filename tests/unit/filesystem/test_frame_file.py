import unittest

from deepstar.filesystem.frame_file import FrameFile


class TestFrameFile(unittest.TestCase):
    """
    This class tests the FrameFile class.
    """

    def test_name(self):
        self.assertEqual(FrameFile.name(1, 'jpg'), '00000001.jpg')

    def test_path(self):
        self.assertEqual(FrameFile.path('test', 1, 'jpg'), 'test/00000001.jpg')

    def test_path_with_res(self):
        self.assertEqual(FrameFile.path('test', 1, 'jpg', '192'), 'test/00000001-192.jpg')  # noqa
