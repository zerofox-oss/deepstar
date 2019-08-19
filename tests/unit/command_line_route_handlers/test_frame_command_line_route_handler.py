from io import StringIO
import mock
import os
import sys
import textwrap
import unittest

from deepstar.command_line_route_handlers.frame_command_line_route_handler \
    import FrameCommandLineRouteHandler
from deepstar.command_line_route_handlers.video_command_line_route_handler \
    import VideoCommandLineRouteHandler
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError

from .. import deepstar_path


class TestFrameCommandLineRouteHandler(unittest.TestCase):
    """
    This class tests the FrameCommandLineRouteHandler class.
    """

    def test_list(self):
        with deepstar_path():
            with mock.patch.dict(os.environ, {'DEBUG_LEVEL': '0'}):
                route_handler = VideoCommandLineRouteHandler()

                video_0001 = os.path.dirname(os.path.realpath(__file__)) + '/../../support/video_0001.mp4'  # noqa

                route_handler.insert_file(video_0001)

                route_handler.select_extract([1])

            args = ['main.py', 'list', 'frame_sets', '1', 'frames']
            opts = {}

            route_handler = FrameCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch.dict(os.environ, {'MODEL_LIST_LENGTH': '2'}):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            expected = textwrap.dedent('''
            5 results
            id | fk_frame_sets | rejected | (width | height)
            ------------------------------------------------
            1 | 1 | 0 | (1280 | 720)
            2 | 1 | 0 | (1280 | 720)
            3 | 1 | 0 | (1280 | 720)
            4 | 1 | 0 | (1280 | 720)
            5 | 1 | 0 | (1280 | 720)''').strip()

            self.assertEqual(actual, expected)

    def test_list_fails_to_select_frame_set(self):
        with deepstar_path():
            with self.assertRaises(CommandLineRouteHandlerError):
                try:
                    FrameCommandLineRouteHandler().list(1)
                except CommandLineRouteHandlerError as e:
                    self.assertEqual(e.message, 'Frame set with ID 00000001 not found')  # noqa

                    raise e

    def test_usage(self):
        with deepstar_path():
            route_handler = FrameCommandLineRouteHandler()

            args = ['main.py', 'usage', 'frames']
            opts = {}

            try:
                sys.stdout = StringIO()
                route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            self.assertTrue('Usage - Frames' in actual)
