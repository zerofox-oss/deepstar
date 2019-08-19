import mock
import os
import unittest

from deepstar.command_line_route_handlers \
     .frame_set_command_line_route_handler import \
     FrameSetCommandLineRouteHandler
from deepstar.command_line_route_handlers \
     .video_command_line_route_handler import \
     VideoCommandLineRouteHandler
from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.plugins.slice_transform_set_select_extract_plugin import \
    SliceTransformSetSelectExtractPlugin

from .. import deepstar_path


class TestSliceTransformSetSelectExtractPlugin(unittest.TestCase):
    """
    This class tests the SliceTransformSetSelectExtractPlugin class.
    """

    def test_transform_set_select_extract_slice(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

            SliceTransformSetSelectExtractPlugin().transform_set_select_extract(1, {'start': '2', 'end': '4'})  # noqa

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'slice', 1, 1))

            result = TransformModel().list(2)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0], (6, 2, 2, None, 0))
            self.assertEqual(result[1], (7, 2, 3, None, 0))
            self.assertEqual(result[2], (8, 2, 4, None, 0))

            # files
            p1 = TransformSetSubDir.path(2)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 6, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 7, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 8, 'jpg')))

    def test_transform_set_select_extract_slice_rejected(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

                TransformModel().update(4, rejected=1)
                TransformModel().update(5, rejected=1)

            SliceTransformSetSelectExtractPlugin().transform_set_select_extract(1, {'start': '2', 'end': '4'})  # noqa

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'slice', 1, 1))

            result = TransformModel().list(2)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], (6, 2, 2, None, 0))
            self.assertEqual(result[1], (7, 2, 3, None, 0))

            # files
            p1 = TransformSetSubDir.path(2)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 6, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 7, 'jpg')))

    def test_transform_set_select_extract_slice_fails_due_to_missing_required_option(self):  # noqa
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})

            with self.assertRaises(ValueError):
                try:
                    SliceTransformSetSelectExtractPlugin().transform_set_select_extract(1, {})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'The start and end options are required but were not supplied')  # noqa

                    raise e
