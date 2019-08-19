import json
import mock
import os
import shutil
import unittest

import cv2

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.filesystem.video_file import VideoFile
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.models.video_model import VideoModel
from deepstar.plugins.default_video_select_extract_plugin import \
    DefaultVideoSelectExtractPlugin
from deepstar.plugins.max_size_transform_set_select_extract_plugin import \
    MaxSizeTransformSetSelectExtractPlugin

from .. import deepstar_path


class TestMaxSizeTransformSetSelectExtractPlugin(unittest.TestCase):
    """
    This class implements tests for the MaxSizeTransformSetSelectExtractPlugin
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

    def test_transform_set_select_extract_max_size(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            self.mock_transform_set()

            with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                transform_set_id = MaxSizeTransformSetSelectExtractPlugin().transform_set_select_extract(1, {})  # noqa

            self.assertEqual(transform_set_id, 2)

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'max_size', 1, 1))

            result = TransformModel().list(2)
            self.assertEqual(len(result), 5)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [6, 2, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [7, 2, 2, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [8, 2, 3, 0])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [9, 2, 4, 0])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [10, 2, 5, 0])

            # files
            p1 = TransformSetSubDir.path(2)

            # transforms
            self.assertEqual(cv2.imread(TransformFile.path(p1, 6, 'jpg')).shape[0], 299)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 7, 'jpg')).shape[0], 299)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 8, 'jpg')).shape[0], 299)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 9, 'jpg')).shape[0], 299)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 10, 'jpg')).shape[0], 299)  # noqa

    def test_transform_set_select_extract_max_size_rejected(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            self.mock_transform_set()

            transform_model = TransformModel()
            transform_model.update(2, rejected=1)
            transform_model.update(4, rejected=1)

            with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                transform_set_id = MaxSizeTransformSetSelectExtractPlugin().transform_set_select_extract(1, {})  # noqa

            self.assertEqual(transform_set_id, 2)

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'max_size', 1, 1))

            result = TransformModel().list(2)
            self.assertEqual(len(result), 3)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [6, 2, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [7, 2, 3, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [8, 2, 5, 0])

            # files
            p1 = TransformSetSubDir.path(2)

            # transforms
            self.assertEqual(cv2.imread(TransformFile.path(p1, 6, 'jpg')).shape[0], 299)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 7, 'jpg')).shape[0], 299)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 8, 'jpg')).shape[0], 299)  # noqa

    def test_transform_set_select_extract_max_size_max_size(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            self.mock_transform_set()

            with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                transform_set_id = MaxSizeTransformSetSelectExtractPlugin().transform_set_select_extract(1, {'max-size': '200'})  # noqa

            self.assertEqual(transform_set_id, 2)

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'max_size', 1, 1))

            result = TransformModel().list(2)
            self.assertEqual(len(result), 5)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [6, 2, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [7, 2, 2, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [8, 2, 3, 0])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [9, 2, 4, 0])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [10, 2, 5, 0])

            # files
            p1 = TransformSetSubDir.path(2)

            # transforms
            self.assertEqual(cv2.imread(TransformFile.path(p1, 6, 'jpg')).shape[0], 200)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 7, 'jpg')).shape[0], 200)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 8, 'jpg')).shape[0], 200)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 9, 'jpg')).shape[0], 200)  # noqa
            self.assertEqual(cv2.imread(TransformFile.path(p1, 10, 'jpg')).shape[0], 200)  # noqa
