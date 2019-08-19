import json
import os
import shutil
import unittest

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.filesystem.video_file import VideoFile
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.models.video_model import VideoModel
from deepstar.plugins.default_video_select_extract_plugin import \
    DefaultVideoSelectExtractPlugin
from deepstar.plugins.max_blur_transform_set_select_curate_plugin import \
    MaxBlurTransformSetSelectCuratePlugin

from .. import deepstar_path


class TestMaxBlurTransformSetSelectCuratePlugin(unittest.TestCase):
    """
    This class tests the MaxBlurTransformSetSelectCuratePlugin class.
    """

    def mock_transform_set(self):
        image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa
        image_0003 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0003.jpg'  # 200-blurry  # noqa
        image_0004 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0004.jpg'  # 200-sharp   # noqa
        image_0005 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0005.jpg'  # 650-blurry  # noqa
        image_0006 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0006.jpg'  # 650-sharp   # noqa

        TransformSetModel().insert('face', 1, None)

        p1 = TransformSetSubDir.path(1)

        os.mkdir(p1)

        transform_model = TransformModel()

        transform_model.insert(1, 1, '{}', 0)
        shutil.copy(image_0001, TransformFile.path(p1, 1, 'jpg'))
        transform_model.insert(1, 2, '{}', 0)
        shutil.copy(image_0003, TransformFile.path(p1, 2, 'jpg'))
        transform_model.insert(1, 3, '{}', 0)
        shutil.copy(image_0004, TransformFile.path(p1, 3, 'jpg'))
        transform_model.insert(1, 4, '{}', 0)
        shutil.copy(image_0005, TransformFile.path(p1, 4, 'jpg'))
        transform_model.insert(1, 5, '{}', 0)
        shutil.copy(image_0006, TransformFile.path(p1, 5, 'jpg'))

    def test_transform_set_select_curate_max_blur(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            self.mock_transform_set()

            MaxBlurTransformSetSelectCuratePlugin().transform_set_select_curate(1, {'max-blur': '100.0'})  # noqa

            # db
            result = TransformSetModel().select(1)
            self.assertEqual(result, (1, 'face', 1, None))

            result = TransformModel().list(1)
            self.assertEqual(len(result), 5)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [1, 1, 1, 1])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [2, 1, 2, 1])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [3, 1, 3, 0])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [4, 1, 4, 1])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [5, 1, 5, 0])

    def test_transform_set_select_curate_max_blur_fails_due_to_missing_required_option(self):  # noqa
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            self.mock_transform_set()

            with self.assertRaises(ValueError):
                try:
                    MaxBlurTransformSetSelectCuratePlugin().transform_set_select_curate(1, {})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'The max-blur option is required but was not supplied')  # noqa

                    raise e
