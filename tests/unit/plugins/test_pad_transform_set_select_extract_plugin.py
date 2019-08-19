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
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.models.video_model import VideoModel
from deepstar.plugins.default_video_select_extract_plugin import \
    DefaultVideoSelectExtractPlugin
from deepstar.plugins.pad_transform_set_select_extract_plugin import \
    PadTransformSetSelectExtractPlugin
from deepstar.plugins.max_size_transform_set_select_extract_plugin import \
    MaxSizeTransformSetSelectExtractPlugin

from .. import deepstar_path


class TestPadTransformSetSelectExtractPlugin(unittest.TestCase):
    """
    This class implements tests for the PadTransformSetSelectExtractPlugin
    class.
    """

    def mock_transform_set(self):
        image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa

        TransformSetModel().insert('face', 1, None)

        p1 = TransformSetSubDir.path(1)

        os.mkdir(p1)

        transform_model = TransformModel()

        for i in range(0, 5):
            transform_model.insert(1, i + 1, '{}', 0)

            shutil.copy(image_0001, TransformFile.path(p1, i + 1, 'jpg'))

    def test_transform_set_select_extract_pad(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            self.mock_transform_set()

            MaxSizeTransformSetSelectExtractPlugin().transform_set_select_extract(1, {})  # noqa

            with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                transform_set_id = PadTransformSetSelectExtractPlugin().transform_set_select_extract(2, {})  # noqa

            self.assertEqual(transform_set_id, 3)

            # db
            result = TransformSetModel().select(3)
            self.assertEqual(result, (3, 'pad', 1, 2))

            result = TransformModel().list(3)
            self.assertEqual(len(result), 5)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [11, 3, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [12, 3, 2, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [13, 3, 3, 0])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [14, 3, 4, 0])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [15, 3, 5, 0])

            # files
            p1 = TransformSetSubDir.path(3)

            # transforms
            self.assertEqual(cv2.imread(TransformFile.path(p1, 11, 'jpg')).shape[:2], (299, 299))  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 12, 'jpg')).shape[:2], (299, 299))  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 13, 'jpg')).shape[:2], (299, 299))  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 14, 'jpg')).shape[:2], (299, 299))  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 15, 'jpg')).shape[:2], (299, 299))  # noqa

    def test_transform_set_select_extract_pad_rejected(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            self.mock_transform_set()

            MaxSizeTransformSetSelectExtractPlugin().transform_set_select_extract(1, {})  # noqa

            transform_model = TransformModel()
            transform_model.update(7, rejected=1)
            transform_model.update(9, rejected=1)

            with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                transform_set_id = PadTransformSetSelectExtractPlugin().transform_set_select_extract(2, {})  # noqa

            self.assertEqual(transform_set_id, 3)

            # db
            result = TransformSetModel().select(3)
            self.assertEqual(result, (3, 'pad', 1, 2))

            result = TransformModel().list(3)
            self.assertEqual(len(result), 3)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [11, 3, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [12, 3, 3, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [13, 3, 5, 0])

            # files
            p1 = TransformSetSubDir.path(3)

            # transforms
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 11, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 12, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 13, 'jpg')), np.ndarray)  # noqa

    def test_transform_set_select_extract_pad_size(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            self.mock_transform_set()

            MaxSizeTransformSetSelectExtractPlugin().transform_set_select_extract(1, {'max-size': '200'})  # noqa

            with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                PadTransformSetSelectExtractPlugin().transform_set_select_extract(2, {'size': '200'})  # noqa

            # db
            result = TransformSetModel().select(3)
            self.assertEqual(result, (3, 'pad', 1, 2))

            result = TransformModel().list(3)
            self.assertEqual(len(result), 5)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [11, 3, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [12, 3, 2, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [13, 3, 3, 0])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [14, 3, 4, 0])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [15, 3, 5, 0])

            # files
            p1 = TransformSetSubDir.path(3)

            # transforms
            self.assertEqual(cv2.imread(TransformFile.path(p1, 11, 'jpg')).shape[:2], (200, 200))  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 12, 'jpg')).shape[:2], (200, 200))  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 13, 'jpg')).shape[:2], (200, 200))  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 14, 'jpg')).shape[:2], (200, 200))  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 15, 'jpg')).shape[:2], (200, 200))  # noqa
