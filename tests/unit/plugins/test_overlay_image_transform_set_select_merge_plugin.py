import mock
import os
import unittest

import cv2
import numpy as np

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
from deepstar.plugins.overlay_image_transform_set_select_merge_plugin import \
    OverlayImageTransformSetSelectMergePlugin

from .. import deepstar_path


class TestOverlayImageTransformSetSelectMergePlugin(unittest.TestCase):
    """
    This class tests the OverlayImageTransformSetSelectMergePlugin class.
    """

    def test_transform_set_select_merge_overlay_image(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})

            image_0007 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0007.png'  # noqa

            OverlayImageTransformSetSelectMergePlugin().transform_set_select_merge([1], {'image-path': image_0007, 'x1': '0', 'y1': '0'})  # noqa

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'overlay_image', None, None))

            result = TransformModel().list(2)
            self.assertEqual(len(result), 5)
            self.assertEqual(result[0], (6, 2, None, None, 0))
            self.assertEqual(result[1], (7, 2, None, None, 0))
            self.assertEqual(result[2], (8, 2, None, None, 0))
            self.assertEqual(result[3], (9, 2, None, None, 0))
            self.assertEqual(result[4], (10, 2, None, None, 0))

            # files
            p1 = TransformSetSubDir.path(2)

            # transforms
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 6, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 7, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 8, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 9, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 10, 'jpg')), np.ndarray)  # noqa

    def test_transform_set_select_merge_overlay_image_rejected(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})

                transform_model = TransformModel()

                transform_model.update(1, rejected=1)

            image_0007 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0007.png'  # noqa

            OverlayImageTransformSetSelectMergePlugin().transform_set_select_merge([1], {'image-path': image_0007, 'x1': '0', 'y1': '0'})  # noqa

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'overlay_image', None, None))

            result = TransformModel().list(2)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], (6, 2, None, None, 0))
            self.assertEqual(result[1], (7, 2, None, None, 0))
            self.assertEqual(result[2], (8, 2, None, None, 0))
            self.assertEqual(result[3], (9, 2, None, None, 0))

            # files
            p1 = TransformSetSubDir.path(2)

            # transforms
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 6, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 7, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 8, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 9, 'jpg')), np.ndarray)  # noqa

    def test_transform_set_select_merge_fade_fails_due_to_transform_set_id_count(self):  # noqa
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})
                route_handler.select_extract([1], 'transform_set', {})

            with self.assertRaises(ValueError):
                try:
                    OverlayImageTransformSetSelectMergePlugin().transform_set_select_merge([1, 2], {})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'Exactly one transform set ID must be supplied')  # noqa

                    raise e

    def test_transform_set_select_merge_fade_fails_due_to_missing_required_option(self):  # noqa
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
                    OverlayImageTransformSetSelectMergePlugin().transform_set_select_merge([1], {})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'The image-path, x1 and y1 options are required but were not supplied')  # noqa

                    raise e

    def test_transform_set_select_merge_fade_fails_due_to_file_not_found(self):  # noqa
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
                    OverlayImageTransformSetSelectMergePlugin().transform_set_select_merge([1], {'image-path': 'test', 'x1': '0', 'y1': '0'})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'The image path test does not exist or is not a file')  # noqa

                    raise e
