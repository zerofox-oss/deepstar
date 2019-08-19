import os
import shutil
import unittest

import cv2
import numpy as np

from deepstar.filesystem.frame_file import FrameFile
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.filesystem.video_file import VideoFile
from deepstar.models.frame_model import FrameModel
from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.video_model import VideoModel
from deepstar.plugins.default_video_select_extract_plugin import \
    DefaultVideoSelectExtractPlugin
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError

from .. import deepstar_path


class TestDefaultVideoSelectExtractPlugin(unittest.TestCase):
    """
    This class tests the DefaultVideoSelectExtractPlugin class.
    """

    def test_video_select_extract(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            frame_set_id = DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa
            self.assertEqual(frame_set_id, 1)

            # db
            result = FrameSetModel().select(1)
            self.assertEqual(result, (1, 1))

            result = FrameModel().list(1)
            self.assertEqual(len(result), 5)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (2, 1, 0))
            self.assertEqual(result[2], (3, 1, 0))
            self.assertEqual(result[3], (4, 1, 0))
            self.assertEqual(result[4], (5, 1, 0))

            # files
            p1 = FrameSetSubDir.path(1)

            # frames
            self.assertIsInstance(cv2.imread(FrameFile.path(p1, 1, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(FrameFile.path(p1, 2, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(FrameFile.path(p1, 3, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(FrameFile.path(p1, 4, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(FrameFile.path(p1, 5, 'jpg')), np.ndarray)  # noqa

            # thumbnails
            self.assertEqual(cv2.imread(FrameFile.path(p1, 1, 'jpg', '192x192')).shape[1], 192)  # noqa
            self.assertEqual(cv2.imread(FrameFile.path(p1, 2, 'jpg', '192x192')).shape[1], 192)  # noqa
            self.assertEqual(cv2.imread(FrameFile.path(p1, 3, 'jpg', '192x192')).shape[1], 192)  # noqa
            self.assertEqual(cv2.imread(FrameFile.path(p1, 4, 'jpg', '192x192')).shape[1], 192)  # noqa
            self.assertEqual(cv2.imread(FrameFile.path(p1, 5, 'jpg', '192x192')).shape[1], 192)  # noqa

    def test_video_select_extract_sub_sample(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1, sub_sample=2)  # noqa

            # db
            result = FrameModel().list(1)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (2, 1, 0))
            self.assertEqual(result[2], (3, 1, 0))

            # files
            p1 = FrameSetSubDir.path(1)

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 3, 'jpg')))

            # thumbnails
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 3, 'jpg', '192x192')))  # noqa

    def test_video_select_extract_max_sample(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1, max_sample=3)  # noqa

            # db
            result = FrameModel().list(1)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (2, 1, 0))
            self.assertEqual(result[2], (3, 1, 0))

            # files
            p1 = FrameSetSubDir.path(1)

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 3, 'jpg')))

            # thumbnails
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 3, 'jpg', '192x192')))  # noqa

    def test_video_select_extract_fails_to_open_video_file(self):
        with deepstar_path():
            with self.assertRaises(CommandLineRouteHandlerError):
                VideoModel().insert('test', 'test')

                DefaultVideoSelectExtractPlugin().video_select_extract(1)
