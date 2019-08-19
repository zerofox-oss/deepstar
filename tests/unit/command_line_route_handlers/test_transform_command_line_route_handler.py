from io import StringIO
import mock
import os
import shutil
import sys
import unittest

from deepstar.command_line_route_handlers \
    .transform_command_line_route_handler \
    import TransformCommandLineRouteHandler
from deepstar.command_line_route_handlers.video_command_line_route_handler \
    import VideoCommandLineRouteHandler
from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError

from .. import deepstar_path


class TestTransformCommandLineRouteHandler(unittest.TestCase):
    """
    This class tests the TransformCommandLineRouteHandler class.
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

    def test_list(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

                self.mock_transform_set()

            args = ['main.py', 'list', 'transform_sets', '1', 'transforms']
            opts = {}

            route_handler = TransformCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = \
                '5 results\n' \
                'id | fk_transform_sets | fk_frames | metadata | rejected | ' \
                '(width | height)\n' \
                '-----------------------------------------------------------' \
                '----------------\n' \
                '1 | 1 | 1 | {} | 0 | (309 | 404)\n' \
                '2 | 1 | 2 | {} | 0 | (309 | 404)\n' \
                '3 | 1 | 3 | {} | 0 | (309 | 404)\n' \
                '4 | 1 | 4 | {} | 0 | (309 | 404)\n' \
                '5 | 1 | 5 | {} | 0 | (309 | 404)'

            self.assertEqual(actual, expected)

    def test_list_fails_to_select_transform_set(self):
        with deepstar_path():
            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    TransformCommandLineRouteHandler().list(1)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Transform set with ID 00000001 not found')  # noqa

                    raise e

    def test_usage(self):
        with deepstar_path():
            route_handler = TransformCommandLineRouteHandler()

            args = ['main.py', 'usage', 'transforms']
            opts = {}

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            self.assertTrue('Usage - Transforms' in actual)
