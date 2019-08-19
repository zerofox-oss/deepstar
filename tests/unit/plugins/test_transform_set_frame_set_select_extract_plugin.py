import mock
import os
import shutil
import unittest

from deepstar.command_line_route_handlers.video_command_line_route_handler \
    import VideoCommandLineRouteHandler
from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.filesystem.video_file import VideoFile
from deepstar.models.frame_model import FrameModel
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.models.video_model import VideoModel
from deepstar.plugins.default_video_select_extract_plugin import \
    DefaultVideoSelectExtractPlugin
from deepstar.plugins.transform_set_frame_set_select_extract_plugin import \
    TransformSetFrameSetSelectExtractPlugin

from .. import deepstar_path


class TestTransformSetFrameSetSelectExtractPlugin(unittest.TestCase):
    """
    This class implements tests for the TransformSetFrameSetSelectExtractPlugin
    class.
    """

    def test_frame_set_select_extract_transform_set(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            plugin = TransformSetFrameSetSelectExtractPlugin()

            transform_set_id = plugin.frame_set_select_extract(1, {})

            self.assertEqual(transform_set_id, 1)

            # db
            result = TransformSetModel().select(1)
            self.assertEqual(result, (1, 'transform_set', 1, None))

            result = TransformModel().list(1)
            self.assertEqual(len(result), 5)
            self.assertEqual(result[0], (1, 1, 1, None, 0))
            self.assertEqual(result[1], (2, 1, 2, None, 0))
            self.assertEqual(result[2], (3, 1, 3, None, 0))
            self.assertEqual(result[3], (4, 1, 4, None, 0))
            self.assertEqual(result[4], (5, 1, 5, None, 0))

            # files
            p1 = TransformSetSubDir.path(transform_set_id)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 3, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 4, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 5, 'jpg')))

    def test_frame_set_select_extract_transform_set_rejected(self):
        with deepstar_path():
            video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

            shutil.copyfile(video_0001, VideoFile.path('video_0001.mp4'))

            VideoModel().insert('test', 'video_0001.mp4')

            DefaultVideoSelectExtractPlugin().video_select_extract(1)  # noqa

            frame_model = FrameModel()
            frame_model.update(2, 1)
            frame_model.update(4, 1)

            transform_set_id = TransformSetFrameSetSelectExtractPlugin().frame_set_select_extract(1, {})  # noqa

            self.assertEqual(transform_set_id, 1)

            # db
            result = TransformSetModel().select(1)
            self.assertEqual(result, (1, 'transform_set', 1, None))

            result = TransformModel().list(1)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (1, 1, 1, None, 0))
            self.assertEqual(result[1], (2, 1, 3, None, 0))
            self.assertEqual(result[2], (3, 1, 5, None, 0))

            # files
            p1 = TransformSetSubDir.path(1)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 3, 'jpg')))
