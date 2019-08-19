from io import StringIO
import json
import mock
import os
import shutil
import sys
import textwrap
import unittest

import cv2

from deepstar.command_line_route_handlers \
    .frame_set_command_line_route_handler import \
    FrameSetCommandLineRouteHandler
from deepstar.command_line_route_handlers \
    .transform_set_command_line_route_handler import \
    TransformSetCommandLineRouteHandler
from deepstar.command_line_route_handlers.video_command_line_route_handler \
    import VideoCommandLineRouteHandler
from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.plugins.plugin import Plugin
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError

from .. import deepstar_path


class TestTransformSetCommandLineRouteHandler(unittest.TestCase):
    """
    This class tests the TransformSetCommandLineRouteHandler class.
    """

    def mock_transform_set(self):
        image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa
        image_0003 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0003.jpg'  # 200-blurry  # noqa
        image_0004 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0004.jpg'  # 200-sharp   # noqa
        image_0005 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0005.jpg'  # 650-blurry  # noqa
        image_0006 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0006.jpg'  # 650-sharp   # noqa

        transform_set_id = TransformSetModel().insert('face', 1, None)

        p1 = TransformSetSubDir.path(transform_set_id)

        os.mkdir(p1)

        transform_model = TransformModel()

        transform_id = transform_model.insert(transform_set_id, 1, '{}', 0)
        shutil.copy(image_0001, TransformFile.path(p1, transform_id, 'jpg'))
        transform_id = transform_model.insert(transform_set_id, 2, '{}', 0)
        shutil.copy(image_0003, TransformFile.path(p1, transform_id, 'jpg'))
        transform_id = transform_model.insert(transform_set_id, 3, '{}', 0)
        shutil.copy(image_0004, TransformFile.path(p1, transform_id, 'jpg'))
        transform_id = transform_model.insert(transform_set_id, 4, '{}', 0)
        shutil.copy(image_0005, TransformFile.path(p1, transform_id, 'jpg'))
        transform_id = transform_model.insert(transform_set_id, 5, '{}', 0)
        shutil.copy(image_0006, TransformFile.path(p1, transform_id, 'jpg'))

    def test_list(self):
        with deepstar_path():
            transform_set_model = TransformSetModel()

            transform_set_model.insert('face', None)
            transform_set_model.insert('face', None)
            transform_set_model.insert('face', None)

            args = ['main.py', 'list', 'transform_sets']
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = textwrap.dedent('''
            3 results
            id | name | fk_frame_sets | fk_prev_transform_sets
            --------------------------------------------------
            1 | face | None | None
            2 | face | None | None
            3 | face | None | None
            ''').strip()

            self.assertEqual(actual, expected)

    def test_select_curate_auto_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            class TestPlugin:
                def transform_set_select_curate(self, transform_set_id, opts):
                    print('test')

            args = ['main.py', 'select', 'transform_sets', '1', 'curate', 'test']  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(Plugin._map, {'transform_set_select_curate': {'test': TestPlugin}}):  # noqa
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'test\nsuccess')

    def test_select_curate_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()
                self.mock_transform_set()
                self.mock_transform_set()

            class TestPlugin:
                def transform_set_select_curate(self, transform_set_id, opts):
                    print('test')

            args = ['main.py', 'select', 'transform_sets', '1-2,3', 'curate', 'test']  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(Plugin._map, {'transform_set_select_curate': {'test': TestPlugin}}):  # noqa
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'test\ntest\ntest\nsuccess')

    def test_select_curate_min_size(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1', 'curate', 'min_size']  # noqa
            opts = {'min-size': '300'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'success')

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
            self.assertEqual(t, [2, 1, 2, 1])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [3, 1, 3, 1])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [4, 1, 4, 0])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [5, 1, 5, 0])

    def test_select_curate_max_blur(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1', 'curate', 'max_blur']  # noqa
            opts = {'max-blur': '100.0'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'success')

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

    def test_select_curate_auto_fails_to_select_a_transform_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'transform_sets', '1', 'curate', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_curate_auto_fails_to_get_a_plugin(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1', 'curate', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, "'test' is not a valid transform set curation plugin name")  # noqa

                    raise e

    def test_select_curate_manual(self):
        pass

    def test_select_curate_manual_fails_to_select_a_transform_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'transform_sets', '1', 'curate', 'manual']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_extract_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            class TestPlugin:
                def transform_set_select_extract(self, transform_set_id, opts):
                    return TransformSetModel().insert('test', TransformSetModel().select(transform_set_id)[2], transform_set_id)  # noqa

            args = ['main.py', 'select', 'transform_sets', '1', 'extract', 'test']  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(Plugin._map, {'transform_set_select_extract': {'test': TestPlugin}}):  # noqa
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=2, name=test, fk_frame_sets=1, fk_prev_transform_sets=1')  # noqa

    def test_select_extract_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()
                self.mock_transform_set()
                self.mock_transform_set()

            class TestPlugin:
                def transform_set_select_extract(self, transform_set_id, opts):
                    return TransformSetModel().insert('test', TransformSetModel().select(transform_set_id)[2], transform_set_id)  # noqa

            args = ['main.py', 'select', 'transform_sets', '1-2,3', 'extract', 'test']  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(Plugin._map, {'transform_set_select_extract': {'test': TestPlugin}}):  # noqa
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = 'transform_set_id=4, name=test, fk_frame_sets=1, ' \
                       'fk_prev_transform_sets=1\n' \
                       'transform_set_id=5, name=test, fk_frame_sets=1, ' \
                       'fk_prev_transform_sets=2\n' \
                       'transform_set_id=6, name=test, fk_frame_sets=1, ' \
                       'fk_prev_transform_sets=3'

            self.assertEqual(actual, expected)

    def test_select_extract_max_size(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1', 'extract', 'max_size']  # noqa
            opts = {'max-size': '200'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=2, name=max_size, fk_frame_sets=1, fk_prev_transform_sets=1')  # noqa

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
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 6, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 7, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 8, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 9, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 10, 'jpg')))

    def test_select_extract_pad(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

                route_handler = TransformSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'max_size', {'max-size': 200})  # noqa

            args = ['main.py', 'select', 'transform_sets', '2', 'extract', 'pad']  # noqa
            opts = {'size': '200'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=3, name=pad, fk_frame_sets=1, fk_prev_transform_sets=2')  # noqa

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
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 11, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 12, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 13, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 14, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 15, 'jpg')))

    def test_select_extract_crop(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

            args = ['main.py', 'select', 'transform_sets', '1', 'extract', 'crop']  # noqa
            opts = {'x1': '0', 'y1': '0', 'x2': '50', 'y2': '50'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=2, name=crop, fk_frame_sets=1, fk_prev_transform_sets=1')  # noqa

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'crop', 1, 1))

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

    def test_select_extract_slice(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

            args = ['main.py', 'select', 'transform_sets', '1', 'extract', 'slice']  # noqa
            opts = {'start': '2', 'end': '4'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=2, name=slice, fk_frame_sets=1, fk_prev_transform_sets=1')  # noqa

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

    def test_select_extract_adjust_color(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

            args = ['main.py', 'select', 'transform_sets', '1', 'extract', 'adjust_color']  # noqa
            opts = {'r': '+10', 'g': '-10', 'b': '+10'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=2, name=adjust_color, fk_frame_sets=1, fk_prev_transform_sets=1')  # noqa

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

    def test_select_extract_fails_to_select_a_transform_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'transform_sets', '1', 'extract', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_extract_fails_to_get_a_plugin(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1', 'extract', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, "'test' is not a valid transform set extraction plugin name")  # noqa

                    raise e

    def test_select_export_dir_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'transform_sets', '1', 'export', 'dir', tmpdir]  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'5 transforms were successfully exported to {tmpdir}')  # noqa

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(tmpdir, 1, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(TransformFile.path(tmpdir, 2, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(TransformFile.path(tmpdir, 3, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(TransformFile.path(tmpdir, 4, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(TransformFile.path(tmpdir, 5, 'jpg')))  # noqa

    def test_select_export_dir_one_rejected(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

                TransformModel().update(5, rejected=1)

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'transform_sets', '1', 'export', 'dir', tmpdir]  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'4 transforms were successfully exported to {tmpdir}')  # noqa

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(tmpdir, 1, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(TransformFile.path(tmpdir, 2, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(TransformFile.path(tmpdir, 3, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(TransformFile.path(tmpdir, 4, 'jpg')))  # noqa

    def test_select_export_dir_one_format(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'transform_sets', '1', 'export', 'dir', tmpdir]  # noqa
            opts = {'format': 'frames%04d.jpg'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'5 transforms were successfully exported to {tmpdir}')  # noqa

            # transforms
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'frames%04d.jpg' % 1)))  # noqa
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'frames%04d.jpg' % 2)))  # noqa
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'frames%04d.jpg' % 3)))  # noqa
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'frames%04d.jpg' % 4)))  # noqa
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'frames%04d.jpg' % 5)))  # noqa

    def test_select_export_dir_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()
                self.mock_transform_set()
                self.mock_transform_set()

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'transform_sets', '1,2-3', 'export', 'dir', tmpdir]  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'15 transforms were successfully exported to {tmpdir}')  # noqa

    def test_select_export_dir_fails_to_select_a_transform_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'transform_sets', '1', 'export', 'dir', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_export_dir_fails_invalid_directory(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1', 'export', 'dir', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'test is not a directory')

                    raise e

    def test_select_export_video_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'transform_sets', '1', 'export', 'video', tmpdir]  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'1 videos were successfully exported to {tmpdir}')  # noqa

            vc = cv2.VideoCapture(os.path.join(tmpdir, '00000001.mp4'))

            try:
                self.assertTrue(vc.isOpened())
                self.assertEqual(vc.get(cv2.CAP_PROP_FRAME_COUNT), 5)
            finally:
                vc.release()

    def test_select_export_video_one_rejected(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})

                TransformModel().update(5, rejected=1)

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'transform_sets', '1', 'export', 'video', tmpdir]  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'1 videos were successfully exported to {tmpdir}')  # noqa

            vc = cv2.VideoCapture(os.path.join(tmpdir, '00000001.mp4'))

            try:
                self.assertTrue(vc.isOpened())
                self.assertEqual(vc.get(cv2.CAP_PROP_FRAME_COUNT), 4)
            finally:
                vc.release()

    def test_select_export_video_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})
                route_handler.select_extract([1], 'transform_set', {})
                route_handler.select_extract([1], 'transform_set', {})

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'transform_sets', '1,2-3', 'export', 'video', tmpdir]  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'3 videos were successfully exported to {tmpdir}')  # noqa

    def test_select_export_video_fails_to_select_a_transform_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'transform_sets', '1', 'export', 'video', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_export_video_fails_invalid_directory(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1', 'export', 'video', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'test is not a directory')

                    raise e

    def test_select_clone_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1', 'clone']
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=2, name=face, fk_frame_sets=1, fk_prev_transform_sets=1')  # noqa

            # db
            result = TransformSetModel().select(2)
            self.assertEqual(result, (2, 'face', 1, 1))

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
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 6, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 7, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 8, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 9, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 10, 'jpg')))

    def test_select_clone_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()
                self.mock_transform_set()
                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1-2,3', 'clone']
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = 'transform_set_id=4, name=face, fk_frame_sets=1, ' \
                       'fk_prev_transform_sets=1\n' \
                       'transform_set_id=5, name=face, fk_frame_sets=1, ' \
                       'fk_prev_transform_sets=2\n' \
                       'transform_set_id=6, name=face, fk_frame_sets=1, ' \
                       'fk_prev_transform_sets=3'

            self.assertEqual(actual, expected)

    def test_select_clone_fails_to_select_a_transform_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'transform_sets', '1', 'clone']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_merge(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()
                self.mock_transform_set()
                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1-2,3', 'merge']
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '4'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=4, name=merge, fk_frame_sets=None, fk_prev_transform_sets=None')  # noqa

            # db
            result = TransformSetModel().select(4)
            self.assertEqual(result, (4, 'merge', None, None))

            result = TransformModel().list(4)
            self.assertEqual(len(result), 15)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [16, 4, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [17, 4, 2, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [18, 4, 3, 0])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [19, 4, 4, 0])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [20, 4, 5, 0])
            t = list(result[5])
            json.loads(t.pop(3))
            self.assertEqual(t, [21, 4, 1, 0])
            t = list(result[6])
            json.loads(t.pop(3))
            self.assertEqual(t, [22, 4, 2, 0])
            t = list(result[7])
            json.loads(t.pop(3))
            self.assertEqual(t, [23, 4, 3, 0])
            t = list(result[8])
            json.loads(t.pop(3))
            self.assertEqual(t, [24, 4, 4, 0])
            t = list(result[9])
            json.loads(t.pop(3))
            self.assertEqual(t, [25, 4, 5, 0])
            t = list(result[10])
            json.loads(t.pop(3))
            self.assertEqual(t, [26, 4, 1, 0])
            t = list(result[11])
            json.loads(t.pop(3))
            self.assertEqual(t, [27, 4, 2, 0])
            t = list(result[12])
            json.loads(t.pop(3))
            self.assertEqual(t, [28, 4, 3, 0])
            t = list(result[13])
            json.loads(t.pop(3))
            self.assertEqual(t, [29, 4, 4, 0])
            t = list(result[14])
            json.loads(t.pop(3))
            self.assertEqual(t, [30, 4, 5, 0])

            # files
            p1 = TransformSetSubDir.path(4)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 16, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 17, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 18, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 19, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 20, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 21, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 22, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 23, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 24, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 25, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 26, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 27, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 28, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 29, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 30, 'jpg')))

    def test_select_merge_rejected(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()
                self.mock_transform_set()
                self.mock_transform_set()

                TransformModel().update(15, rejected=1)

            args = ['main.py', 'select', 'transform_sets', '1-2,3', 'merge']
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '4'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=4, name=merge, fk_frame_sets=None, fk_prev_transform_sets=None')  # noqa

            # db
            result = TransformSetModel().select(4)
            self.assertEqual(result, (4, 'merge', None, None))

            result = TransformModel().list(4)
            self.assertEqual(len(result), 14)
            t = list(result[0])
            json.loads(t.pop(3))
            self.assertEqual(t, [16, 4, 1, 0])
            t = list(result[1])
            json.loads(t.pop(3))
            self.assertEqual(t, [17, 4, 2, 0])
            t = list(result[2])
            json.loads(t.pop(3))
            self.assertEqual(t, [18, 4, 3, 0])
            t = list(result[3])
            json.loads(t.pop(3))
            self.assertEqual(t, [19, 4, 4, 0])
            t = list(result[4])
            json.loads(t.pop(3))
            self.assertEqual(t, [20, 4, 5, 0])
            t = list(result[5])
            json.loads(t.pop(3))
            self.assertEqual(t, [21, 4, 1, 0])
            t = list(result[6])
            json.loads(t.pop(3))
            self.assertEqual(t, [22, 4, 2, 0])
            t = list(result[7])
            json.loads(t.pop(3))
            self.assertEqual(t, [23, 4, 3, 0])
            t = list(result[8])
            json.loads(t.pop(3))
            self.assertEqual(t, [24, 4, 4, 0])
            t = list(result[9])
            json.loads(t.pop(3))
            self.assertEqual(t, [25, 4, 5, 0])
            t = list(result[10])
            json.loads(t.pop(3))
            self.assertEqual(t, [26, 4, 1, 0])
            t = list(result[11])
            json.loads(t.pop(3))
            self.assertEqual(t, [27, 4, 2, 0])
            t = list(result[12])
            json.loads(t.pop(3))
            self.assertEqual(t, [28, 4, 3, 0])
            t = list(result[13])
            json.loads(t.pop(3))
            self.assertEqual(t, [29, 4, 4, 0])

            # files
            p1 = TransformSetSubDir.path(4)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 16, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 17, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 18, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 19, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 20, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 21, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 22, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 23, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 24, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 25, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 26, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 27, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 28, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 29, 'jpg')))

    def test_select_merge_fails_to_select_a_transform_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'transform_sets', '1,2', 'merge']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_merge_non_default_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameSetCommandLineRouteHandler().select_extract([1], 'transform_set', {})  # noqa

            class TestPlugin:
                def transform_set_select_merge(self, transform_set_ids, opts):
                    return TransformSetModel().insert('test', None, None)

            args = ['main.py', 'select', 'transform_sets', '1', 'merge', 'test']  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(Plugin._map, {'transform_set_select_merge': {'test': TestPlugin}}):  # noqa
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=2, name=test, fk_frame_sets=None, fk_prev_transform_sets=None')  # noqa

    def test_select_merge_non_default_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})
                route_handler.select_extract([1], 'transform_set', {})
                route_handler.select_extract([1], 'transform_set', {})

            class TestPlugin:
                def transform_set_select_merge(self, transform_set_ids, opts):
                    return TransformSetModel().insert('test', None, None)

            args = ['main.py', 'select', 'transform_sets', '1-2,3', 'merge', 'test']  # noqa
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(Plugin._map, {'transform_set_select_merge': {'test': TestPlugin}}):  # noqa
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=4, name=test, fk_frame_sets=None, fk_prev_transform_sets=None')  # noqa

    def test_select_merge_fade(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})
                route_handler.select_extract([1], 'transform_set', {})

            args = ['main.py', 'select', 'transform_sets', '1,2', 'merge', 'fade']  # noqa
            opts = {'frame-count': '2'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=3, name=fade, fk_frame_sets=None, fk_prev_transform_sets=None')  # noqa

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
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 11, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 12, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 13, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 14, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 15, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 16, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 17, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 18, 'jpg')))

    def test_select_merge_overlay(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})
                route_handler.select_extract([1], 'transform_set', {})

            args = ['main.py', 'select', 'transform_sets', '1,2', 'merge', 'overlay']  # noqa
            opts = {'x1': '0', 'y1': '0'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=3, name=overlay, fk_frame_sets=None, fk_prev_transform_sets=None')  # noqa

            # db
            result = TransformSetModel().select(3)
            self.assertEqual(result, (3, 'overlay', None, None))

            result = TransformModel().list(3)
            self.assertEqual(len(result), 5)
            self.assertEqual(result[0], (11, 3, None, None, 0))
            self.assertEqual(result[1], (12, 3, None, None, 0))
            self.assertEqual(result[2], (13, 3, None, None, 0))
            self.assertEqual(result[3], (14, 3, None, None, 0))
            self.assertEqual(result[4], (15, 3, None, None, 0))

            # files
            p1 = TransformSetSubDir.path(3)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 11, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 12, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 13, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 14, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 15, 'jpg')))

    def test_select_merge_overlay_image(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                route_handler = FrameSetCommandLineRouteHandler()

                route_handler.select_extract([1], 'transform_set', {})

            args = ['main.py', 'select', 'transform_sets', '1', 'merge', 'overlay_image']  # noqa

            image_0007 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0007.png'  # noqa

            opts = {'image-path': image_0007, 'x1': '0', 'y1': '0'}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=2, name=overlay_image, fk_frame_sets=None, fk_prev_transform_sets=None')  # noqa

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
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 6, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 7, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 8, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 9, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 10, 'jpg')))

    def test_select_merge_non_default_fails_to_select_a_transform_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'transform_sets', '1', 'merge', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_merge_non_default_fails_to_get_a_plugin(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'select', 'transform_sets', '1', 'merge', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, "'test' is not a valid transform set merge plugin name")  # noqa

                    raise e

    def test_delete_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            # files
            self.assertTrue(os.path.exists(TransformSetSubDir.path(1)))

            # db
            transform_set_model = TransformSetModel()

            self.assertIsNotNone(transform_set_model.select(1))

            transform_model = TransformModel()

            self.assertIsNotNone(transform_model.select(1))
            self.assertIsNotNone(transform_model.select(2))
            self.assertIsNotNone(transform_model.select(3))
            self.assertIsNotNone(transform_model.select(4))
            self.assertIsNotNone(transform_model.select(5))

            args = ['main.py', 'delete', 'transform_sets', '1']
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'Transform set 1 was successfully deleted')  # noqa

            # db
            self.assertIsNone(transform_set_model.select(1))

            self.assertIsNone(transform_model.select(1))
            self.assertIsNone(transform_model.select(2))
            self.assertIsNone(transform_model.select(3))
            self.assertIsNone(transform_model.select(4))
            self.assertIsNone(transform_model.select(5))

            # files
            self.assertFalse(os.path.exists(TransformSetSubDir.path(1)))

    def test_delete_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()
                self.mock_transform_set()
                self.mock_transform_set()

            args = ['main.py', 'delete', 'transform_sets', '1-2,3']
            opts = {}

            route_handler = TransformSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = textwrap.dedent('''
            Transform set 1 was successfully deleted
            Transform set 2 was successfully deleted
            Transform set 3 was successfully deleted''').strip()

            self.assertEqual(actual, expected)

    def test_delete_fails_to_select_transform_set(self):
        with deepstar_path():
            args = ['main.py', 'delete', 'transform_sets', '1']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_usage(self):
        with deepstar_path():
            route_handler = TransformSetCommandLineRouteHandler()

            args = ['main.py', 'usage', 'transform_sets']
            opts = {}

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

        self.assertTrue('Usage - Transform Sets' in actual)
