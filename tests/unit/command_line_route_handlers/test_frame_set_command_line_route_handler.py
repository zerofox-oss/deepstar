from io import StringIO
import json
import mock
import os
import shutil
import sys
import textwrap
import unittest

from deepstar.filesystem.frame_file import FrameFile
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.frame_model import FrameModel
from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.models.video_model import VideoModel
from deepstar.plugins.plugin import Plugin
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError
from deepstar.command_line_route_handlers \
    .frame_set_command_line_route_handler \
    import FrameSetCommandLineRouteHandler
from deepstar.command_line_route_handlers.video_command_line_route_handler \
    import VideoCommandLineRouteHandler

from .. import deepstar_path


class TestFrameSetCommandLineRouteHandler(unittest.TestCase):
    """
    This class tests the FrameSetCommandLineRouteHandler class.
    """

    def test_list(self):
        with deepstar_path():
            video_model = VideoModel()
            video_model.insert('test1', 'test2')
            video_model.insert('test3', 'test4')
            video_model.insert('test5', 'test6')

            frame_set_model = FrameSetModel()
            frame_set_model.insert(1)
            frame_set_model.insert(2)
            frame_set_model.insert(3)

            args = ['main.py', 'list', 'frame_sets']
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = textwrap.dedent('''
            3 results
            id | fk_videos
            -------------
            1 | 1
            2 | 2
            3 | 3''').strip()

            self.assertEqual(actual, expected)

    def test_select_curate_manual(self):
        pass

    def test_select_curate_manual_fails_to_select_a_frame_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'frame_sets', '1', 'curate', 'manual']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    FrameSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Frame set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_extract_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            class TestPlugin:
                def frame_set_select_extract(self, frame_set_id, opts):
                    return TransformSetModel().insert('test', frame_set_id, None)  # noqa

            args = ['main.py', 'select', 'frame_sets', '1', 'extract', 'test']  # noqa
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(Plugin._map, {'frame_set_select_extract': {'test': TestPlugin}}):  # noqa
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=1, name=test, fk_frame_sets=1, fk_prev_transform_sets=None')  # noqa

    def test_select_extract_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)

                route_handler.select_extract([1, 2, 3])

            class TestPlugin:
                def frame_set_select_extract(self, frame_set_id, opts):
                    return TransformSetModel().insert('test', frame_set_id, None)  # noqa

            args = ['main.py', 'select', 'frame_sets', '1-2,3', 'extract', 'test']  # noqa
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(Plugin._map, {'frame_set_select_extract': {'test': TestPlugin}}):  # noqa
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = 'transform_set_id=1, name=test, fk_frame_sets=1, ' \
                       'fk_prev_transform_sets=None\n' \
                       'transform_set_id=2, name=test, fk_frame_sets=2, ' \
                       'fk_prev_transform_sets=None\n' \
                       'transform_set_id=3, name=test, fk_frame_sets=3, ' \
                       'fk_prev_transform_sets=None'

            self.assertEqual(actual, expected)

    def test_select_extract_face(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            args = ['main.py', 'select', 'frame_sets', '1', 'extract', 'face']  # noqa
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=1, name=face, fk_frame_sets=1, fk_prev_transform_sets=None')  # noqa

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
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 3, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 4, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 5, 'jpg')))

    def test_select_extract_transform_set(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            args = ['main.py', 'select', 'frame_sets', '1', 'extract', 'transform_set']  # noqa
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'transform_set_id=1, name=transform_set, fk_frame_sets=1, fk_prev_transform_sets=None')  # noqa

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
            p1 = TransformSetSubDir.path(1)

            # transforms
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 3, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 4, 'jpg')))
            self.assertTrue(os.path.isfile(TransformFile.path(p1, 5, 'jpg')))

    def test_select_extract_fails_to_select_a_frame_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'frame_sets', '1', 'extract', 'test']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    FrameSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Frame set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_extract_fails_to_get_a_plugin(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            args = ['main.py', 'select', 'frame_sets', '1', 'extract', 'test']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    FrameSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, "'test' is not a valid frame set extraction plugin name")  # noqa

                    raise e

    def test_delete_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            # files
            self.assertTrue(os.path.exists(FrameSetSubDir.path(1)))

            # db
            frame_set_model = FrameSetModel()

            self.assertIsNotNone(frame_set_model.select(1))

            frame_model = FrameModel()

            self.assertIsNotNone(frame_model.select(1))
            self.assertIsNotNone(frame_model.select(2))
            self.assertIsNotNone(frame_model.select(3))
            self.assertIsNotNone(frame_model.select(4))
            self.assertIsNotNone(frame_model.select(5))

            args = ['main.py', 'delete', 'frame_sets', '1']
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'Frame set 1 was successfully deleted')

            # db
            self.assertIsNone(frame_set_model.select(1))

            self.assertIsNone(frame_model.select(1))
            self.assertIsNone(frame_model.select(2))
            self.assertIsNone(frame_model.select(3))
            self.assertIsNone(frame_model.select(4))
            self.assertIsNone(frame_model.select(5))

            # files
            self.assertFalse(os.path.exists(FrameSetSubDir.path(1)))

    def test_delete_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)

                route_handler.select_extract([1, 2, 3])

            args = ['main.py', 'delete', 'frame_sets', '1-2,3']
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = textwrap.dedent('''
            Frame set 1 was successfully deleted
            Frame set 2 was successfully deleted
            Frame set 3 was successfully deleted''').strip()

            self.assertEqual(actual, expected)

    def test_delete_fails_to_select_a_frame_set(self):
        with deepstar_path():
            args = ['main.py', 'delete', 'frame_sets', '1']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    FrameSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Frame set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_clone_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            args = ['main.py', 'select', 'frame_sets', '1', 'clone']
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '4'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'frame_set_id=2, fk_videos=1')

            # db
            result = FrameSetModel().select(2)
            self.assertEqual(result, (2, 1))

            result = FrameModel().list(2)
            self.assertEqual(len(result), 5)
            self.assertEqual(result[0], (6, 2, 0))
            self.assertEqual(result[1], (7, 2, 0))
            self.assertEqual(result[2], (8, 2, 0))
            self.assertEqual(result[3], (9, 2, 0))
            self.assertEqual(result[4], (10, 2, 0))

            # files
            p1 = FrameSetSubDir.path(2)

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 6, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 7, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 8, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 9, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 10, 'jpg')))

            # thumbnails
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 6, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 7, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 8, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 9, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 10, 'jpg', '192x192')))  # noqa

    def test_select_clone_many(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)

                route_handler.select_extract([1, 2, 3])

            args = ['main.py', 'select', 'frame_sets', '1-2,3', 'clone']
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = textwrap.dedent('''
            frame_set_id=4, fk_videos=1
            frame_set_id=5, fk_videos=2
            frame_set_id=6, fk_videos=3''').strip()

            self.assertEqual(actual, expected)

    def test_select_clone_fails_to_select_a_frame_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'frame_sets', '1', 'clone']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    FrameSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Frame set with ID 00000001 not found')  # noqa

                    raise e

    def test_select_merge(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)

                route_handler.select_extract([1, 2, 3])

            args = ['main.py', 'select', 'frame_sets', '1-2,3', 'merge']
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '4'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'frame_set_id=4, fk_videos=None')

            # db
            result = FrameSetModel().select(4)
            self.assertEqual(result, (4, None))

            result = FrameModel().list(4)
            self.assertEqual(len(result), 15)
            self.assertEqual(result[0], (16, 4, 0))
            self.assertEqual(result[1], (17, 4, 0))
            self.assertEqual(result[2], (18, 4, 0))
            self.assertEqual(result[3], (19, 4, 0))
            self.assertEqual(result[4], (20, 4, 0))
            self.assertEqual(result[5], (21, 4, 0))
            self.assertEqual(result[6], (22, 4, 0))
            self.assertEqual(result[7], (23, 4, 0))
            self.assertEqual(result[8], (24, 4, 0))
            self.assertEqual(result[9], (25, 4, 0))
            self.assertEqual(result[10], (26, 4, 0))
            self.assertEqual(result[11], (27, 4, 0))
            self.assertEqual(result[12], (28, 4, 0))
            self.assertEqual(result[13], (29, 4, 0))
            self.assertEqual(result[14], (30, 4, 0))

            # files
            p1 = FrameSetSubDir.path(4)

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 16, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 17, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 18, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 19, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 20, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 21, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 22, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 23, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 24, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 25, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 26, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 27, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 28, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 29, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 30, 'jpg')))

            # thumbnails
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 16, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 17, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 18, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 19, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 20, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 21, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 22, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 23, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 24, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 25, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 26, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 27, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 28, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 29, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 30, 'jpg', '192x192')))  # noqa

    def test_select_merge_rejected(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)
                route_handler.insert_file(video_0001)

                route_handler.select_extract([1, 2, 3])

                FrameModel().update(15, rejected=1)

            args = ['main.py', 'select', 'frame_sets', '1-2,3', 'merge']
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '4'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'frame_set_id=4, fk_videos=None')

            # db
            result = FrameSetModel().select(4)
            self.assertEqual(result, (4, None))

            result = FrameModel().list(4)
            self.assertEqual(len(result), 14)
            self.assertEqual(result[0], (16, 4, 0))
            self.assertEqual(result[1], (17, 4, 0))
            self.assertEqual(result[2], (18, 4, 0))
            self.assertEqual(result[3], (19, 4, 0))
            self.assertEqual(result[4], (20, 4, 0))
            self.assertEqual(result[5], (21, 4, 0))
            self.assertEqual(result[6], (22, 4, 0))
            self.assertEqual(result[7], (23, 4, 0))
            self.assertEqual(result[8], (24, 4, 0))
            self.assertEqual(result[9], (25, 4, 0))
            self.assertEqual(result[10], (26, 4, 0))
            self.assertEqual(result[11], (27, 4, 0))
            self.assertEqual(result[12], (28, 4, 0))
            self.assertEqual(result[13], (29, 4, 0))

            # files
            p1 = FrameSetSubDir.path(4)

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 16, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 17, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 18, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 19, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 20, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 21, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 22, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 23, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 24, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 25, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 26, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 27, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 28, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 29, 'jpg')))

            # thumbnails
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 16, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 17, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 18, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 19, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 20, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 21, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 22, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 23, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 24, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 25, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 26, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 27, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 28, 'jpg', '192x192')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 29, 'jpg', '192x192')))  # noqa

    def test_select_merge_fails_to_select_a_frame_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'frame_sets', '1,2', 'merge']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    FrameSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Frame set with ID 00000001 not found')  # noqa

                    raise e

    def test_insert_images(self):
        with deepstar_path():
            image_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0001.jpg'  # noqa
            image_0007 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/image_0007.png'  # noqa

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            shutil.copy(image_0001, os.path.join(tmpdir, 'image_0001.jpg'))
            shutil.copy(image_0001, os.path.join(tmpdir, 'image_0002.jpg'))
            shutil.copy(image_0007, os.path.join(tmpdir, 'image_0003.png'))
            shutil.copy(image_0007, os.path.join(tmpdir, 'image_0004.png'))

            args = ['main.py', 'insert', 'frame_sets', 'images', tmpdir]
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'frame_set_id=1, fk_videos=None')

            # db
            result = FrameSetModel().select(1)
            self.assertEqual(result, (1, None))
            result = FrameModel().list(1)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], (1, 1, 0))
            self.assertEqual(result[1], (2, 1, 0))
            self.assertEqual(result[2], (3, 1, 0))
            self.assertEqual(result[3], (4, 1, 0))

            # files
            p1 = FrameSetSubDir.path(1)

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 1, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 2, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 3, 'jpg')))
            self.assertTrue(os.path.isfile(FrameFile.path(p1, 4, 'jpg')))

    def test_insert_images_does_not_insert_non_images(self):
        with deepstar_path():
            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            with open(os.path.join(tmpdir, 'test'), 'w') as file_:
                file_.write('test')

            with open(os.path.join(tmpdir, 'test.txt'), 'w') as file_:
                file_.write('test')

            args = ['main.py', 'insert', 'frame_sets', 'images', tmpdir]
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'frame_set_id=1, fk_videos=None')

            # db
            result = FrameSetModel().select(1)
            self.assertEqual(result, (1, None))
            result = FrameModel().list(0)

    def test_insert_images_fails_due_to_isdir_fails(self):
        with deepstar_path():
            args = ['main.py', 'insert', 'frame_sets', 'images', 'test']
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    FrameSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'The path at test is not a directory')  # noqa

                    raise e

    def test_select_export_dir_one(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'frame_sets', '1', 'export', 'dir', tmpdir]  # noqa
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'5 frames were successfully exported to {tmpdir}')  # noqa

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(tmpdir, 1, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(tmpdir, 2, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(tmpdir, 3, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(tmpdir, 4, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(tmpdir, 5, 'jpg')))  # noqa

    def test_select_export_dir_one_rejected(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                FrameModel().update(5, rejected=1)

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'frame_sets', '1', 'export', 'dir', tmpdir]  # noqa
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'4 frames were successfully exported to {tmpdir}')  # noqa

            # frames
            self.assertTrue(os.path.isfile(FrameFile.path(tmpdir, 1, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(tmpdir, 2, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(tmpdir, 3, 'jpg')))  # noqa
            self.assertTrue(os.path.isfile(FrameFile.path(tmpdir, 4, 'jpg')))  # noqa

    def test_select_export_dir_one_format(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'frame_sets', '1', 'export', 'dir', tmpdir]  # noqa
            opts = {'format': 'frames%04d.jpg'}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'5 frames were successfully exported to {tmpdir}')  # noqa

            # frames
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
                route_handler.select_extract([1])
                route_handler.select_extract([1])

            tmpdir = os.environ['DEEPSTAR_PATH'] + '/test'

            os.mkdir(tmpdir)

            args = ['main.py', 'select', 'frame_sets', '1,2-3', 'export', 'dir', tmpdir]  # noqa
            opts = {}

            route_handler = FrameSetCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, f'15 frames were successfully exported to {tmpdir}')  # noqa

    def test_select_export_dir_fails_to_select_a_frame_set(self):
        with deepstar_path():
            args = ['main.py', 'select', 'frame_sets', '1', 'export', 'dir', 'test']  # noqa
            opts = {}

            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    FrameSetCommandLineRouteHandler().handle(args, opts)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Frame set with ID 00000001 not found')  # noqa

                    raise e

    def test_usage(self):
        with deepstar_path():
            route_handler = FrameSetCommandLineRouteHandler()

            args = ['main.py', 'usage', 'frame_sets']
            opts = {}

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            self.assertTrue('Usage - Frame Sets' in actual)
