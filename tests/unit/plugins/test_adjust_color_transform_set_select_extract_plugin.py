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
from deepstar.plugins.adjust_color_transform_set_select_extract_plugin import \
     AdjustColorTransformSetSelectExtractPlugin

from .. import deepstar_path


class TestAdjustColorTransformSetSelectExtractPlugin(unittest.TestCase):
    """
    This class tests the CropTransformSetSelectExtractPlugin class.
    """

    def test_transform_set_select_extract_adjust_color(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

            AdjustColorTransformSetSelectExtractPlugin().transform_set_select_extract(1, {'r': '+10', 'g': '-10', 'b': '+10'})  # noqa

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'adjust_color', 1, 1))

            result = TransformModel().list(2)
            self.assertEqual(len(result), 5)
            self.assertEqual(result[0], (6, 2, 1, None, 0))
            self.assertEqual(result[1], (7, 2, 2, None, 0))
            self.assertEqual(result[2], (8, 2, 3, None, 0))
            self.assertEqual(result[3], (9, 2, 4, None, 0))
            self.assertEqual(result[4], (10, 2, 5, None, 0))

            # files
            p1 = TransformSetSubDir.path(2)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 6, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 7, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 8, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 9, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 10, 'jpg')))

    def test_transform_set_select_extract_adjust_color_rejected(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

                TransformModel().update(5, rejected=1)

            AdjustColorTransformSetSelectExtractPlugin().transform_set_select_extract(1, {'r': '+10', 'g': '-10', 'b': '+10'})  # noqa

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'adjust_color', 1, 1))

            result = TransformModel().list(2)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], (6, 2, 1, None, 0))
            self.assertEqual(result[1], (7, 2, 2, None, 0))
            self.assertEqual(result[2], (8, 2, 3, None, 0))
            self.assertEqual(result[3], (9, 2, 4, None, 0))

            # files
            p1 = TransformSetSubDir.path(2)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 6, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 7, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 8, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 9, 'jpg')))

    def test_transform_set_select_extract_adjust_color_fails_due_to_missing_required_option(self):  # noqa
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

            with self.assertRaises(ValueError):
                try:
                    AdjustColorTransformSetSelectExtractPlugin().transform_set_select_extract(1, {})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'The r, g and/or b options are required but were not supplied')  # noqa

                    raise e

    def test_transform_set_select_extract_adjust_color_fails_due_to_option_value_format(self):  # noqa
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

            with self.assertRaises(ValueError):
                try:
                    AdjustColorTransformSetSelectExtractPlugin().transform_set_select_extract(1, {'r': 'test'})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'A color adjustment option value must be formatted as +/- followed by a number (e.g. --r=+10)')  # noqa

                    raise e
