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
from deepstar.plugins.fade_transform_set_select_merge_plugin import \
    FadeTransformSetSelectMergePlugin

from .. import deepstar_path


class TestFadeTransformSetSelectMergePlugin(unittest.TestCase):
    """
    This class tests the FadeTransformSetSelectMergePlugin class.
    """

    def test_transform_set_select_merge_fade(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})
                route_handler.select_extract([1], 'transform_set', {})

            FadeTransformSetSelectMergePlugin().transform_set_select_merge([1, 2], {'frame-count': '2'})  # noqa

            # db
            result = TransformSetModel().select(3)
            self.assertEqual(result, (3, 'fade', None, None))

            result = TransformModel().list(3)
            self.assertEqual(len(result), 8)
            self.assertEqual(result[0], (11, 3, 1, None, 0))
            self.assertEqual(result[1], (12, 3, 2, None, 0))
            self.assertEqual(result[2], (13, 3, 3, None, 0))
            self.assertEqual(result[3], (14, 3, None, None, 0))
            self.assertEqual(result[4], (15, 3, None, None, 0))
            self.assertEqual(result[5], (16, 3, 3, None, 0))
            self.assertEqual(result[6], (17, 3, 4, None, 0))
            self.assertEqual(result[7], (18, 3, 5, None, 0))

            # files
            p1 = TransformSetSubDir.path(3)

            # transforms
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 11, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 12, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 13, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 14, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 15, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 16, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 17, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 18, 'jpg')), np.ndarray)  # noqa

    def test_transform_set_select_merge_fade_rejected(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})
                route_handler.select_extract([1], 'transform_set', {})

                transform_model = TransformModel()

                transform_model.update(1, rejected=1)
                transform_model.update(10, rejected=1)

            FadeTransformSetSelectMergePlugin().transform_set_select_merge([1, 2], {'frame-count': '2'})  # noqa

            # db
            result = TransformSetModel().select(3)
            self.assertEqual(result, (3, 'fade', None, None))

            result = TransformModel().list(3)
            self.assertEqual(len(result), 6)
            self.assertEqual(result[0], (11, 3, 2, None, 0))
            self.assertEqual(result[1], (12, 3, 3, None, 0))
            self.assertEqual(result[2], (13, 3, None, None, 0))
            self.assertEqual(result[3], (14, 3, None, None, 0))
            self.assertEqual(result[4], (15, 3, 3, None, 0))
            self.assertEqual(result[5], (16, 3, 4, None, 0))

            # files
            p1 = TransformSetSubDir.path(3)

            # transforms
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 11, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 12, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 13, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 14, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 15, 'jpg')), np.ndarray)  # noqa
            self.assertIsInstance(cv2.imread(TransformFile.path(p1, 16, 'jpg')), np.ndarray)  # noqa

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
                    FadeTransformSetSelectMergePlugin().transform_set_select_merge([1, 2, 3], {})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'Exactly two transform set IDs must be supplied')  # noqa

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
                route_handler.select_extract([1], 'transform_set', {})

            with self.assertRaises(ValueError):
                try:
                    FadeTransformSetSelectMergePlugin().transform_set_select_merge([1, 2], {})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'The frame-count option is required but was not supplied')  # noqa

                    raise e

    def test_transform_set_select_merge_fade_fails_due_to_frame_count_less_than_one(self):  # noqa
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
                    FadeTransformSetSelectMergePlugin().transform_set_select_merge([1, 2], {'frame-count': '0'})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'Frame count must be 1 or greater')  # noqa

                    raise e

    def test_transform_set_select_merge_fade_fails_due_to_transform_set_count_less_than_frame_count(self):  # noqa
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
                    FadeTransformSetSelectMergePlugin().transform_set_select_merge([1, 2], {'frame-count': '6'})  # noqa
                except ValueError as e:
                    self.assertEqual(str(e), 'Both transform sets must be greater than frame count')  # noqa

                    raise e
