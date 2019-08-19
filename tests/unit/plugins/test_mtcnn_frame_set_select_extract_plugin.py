import json
import mock
import os
import shutil
import unittest

import cv2
import numpy as np

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.filesystem.video_file import VideoFile
from deepstar.models.frame_model import FrameModel
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.models.video_model import VideoModel
from deepstar.plugins.default_video_select_extract_plugin import \
    DefaultVideoSelectExtractPlugin
from deepstar.plugins.mtcnn_frame_set_select_extract_plugin import \
    MTCNNFrameSetSelectExtractPlugin

from .. import deepstar_path


class TestMTCNNFrameSetSelectExtractPlugin(unittest.TestCase):
    """
    This class implements tests for the MTCNNFrameSetSelectExtractPlugin class.
    """

    def test_frame_set_select_extract_face(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                transform_set_id = MTCNNFrameSetSelectExtractPlugin().frame_set_select_extract(1, {})  # noqa

            self.assertEqual(transform_set_id, 1)

            # db
            result = TransformSetModel().select(1)
            self.assertEqual(result, (1, 'face', 1, None))

            result = TransformModel().list(1)
            self.assertEqual(len(result), 5)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [1, 1, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [2, 1, 2, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [3, 1, 3, 0])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [4, 1, 4, 0])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [5, 1, 5, 0])

            # files
            p1 = TransformSetSubDir.path(1)

            # transforms
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 1, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 2, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 3, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 4, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 5, 'jpg')), np.ndarray)  # noqa

    def test_frame_set_select_extract_face_rejected(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            frame_model = FrameModel()
            frame_model.update(2, 1)
            frame_model.update(4, 1)

            with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                transform_set_id = MTCNNFrameSetSelectExtractPlugin().frame_set_select_extract(1, {})  # noqa

            self.assertEqual(transform_set_id, 1)

            # db
            result = TransformSetModel().select(1)
            self.assertEqual(result, (1, 'face', 1, None))

            result = TransformModel().list(1)
            self.assertEqual(len(result), 3)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [1, 1, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [2, 1, 3, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [3, 1, 5, 0])

            # files
            p1 = TransformSetSubDir.path(1)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 3, 'jpg')))

    def test_frame_set_select_extract_face_debug(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                transform_set_id = MTCNNFrameSetSelectExtractPlugin().frame_set_select_extract(1, {'debug': True})  # noqa

            self.assertEqual(transform_set_id, 1)

            # db
            result = TransformSetModel().select(1)
            self.assertEqual(result, (1, 'face', 1, None))

            result = TransformModel().list(1)
            self.assertEqual(len(result), 5)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [1, 1, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [2, 1, 2, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [3, 1, 3, 0])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [4, 1, 4, 0])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [5, 1, 5, 0])

            # files
            p1 = TransformSetSubDir.path(1)

            # transforms
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 1, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 2, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 3, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 4, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 5, 'jpg')), np.ndarray)  # noqa
