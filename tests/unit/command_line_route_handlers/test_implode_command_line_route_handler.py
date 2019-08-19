from io import StringIO
import mock
import os
import sys
import unittest

from deepstar.command_line_route_handlers.implode_command_line_route_handler \
    import ImplodeCommandLineRouteHandler
from deepstar.filesystem.db_dir import DBDir
from deepstar.filesystem.file_dir import FileDir

from .. import deepstar_path


class TestImplodeCommandLineRouteHandler(unittest.TestCase):
    """
    This class tests the ImplodeCommandLineRouteHandler class.
    """

    def test_implodes(self):
        with deepstar_path():
            # exist
            for path in [DBDir.path(), FileDir.path()]:
                self.assertTrue(os.path.isdir(path))

            def mock_input(q):
                q_ = f'Are you sure you want to implode the deepstar path ' \
                     f'{os.environ["DEEPSTAR_PATH"]} [y/n]? '

                self.assertEqual(q, q_)

                return 'y'

            args = ['main.py', 'implode']
            opts = {}

            route_handler = ImplodeCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch('builtins.input', side_effect=mock_input):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'The deepstar path was succesfully imploded')  # noqa

            # files

            # do not exist
            for path in [DBDir.path(), FileDir.path()]:
                self.assertFalse(os.path.isdir(path))

    def test_does_not_implode(self):
        with deepstar_path():
            # exist
            for path in [DBDir.path(), FileDir.path()]:
                self.assertTrue(os.path.isdir(path))

            def mock_input(q):
                q_ = f'Are you sure you want to implode the deepstar path ' \
                     f'{os.environ["DEEPSTAR_PATH"]} [y/n]? '

                self.assertEqual(q, q_)

                return 'n'

            args = ['main.py', 'implode']
            opts = {}

            route_handler = ImplodeCommandLineRouteHandler()

            try:
                sys.stdout = StringIO()
                with mock.patch('builtins.input', side_effect=mock_input):
                    route_handler.handle(args, opts)
                actual = sys.stdout.getvalue().strip()
            finally:
                sys.stdout = sys.__stdout__

            # stdout
            self.assertEqual(actual, 'The deepstar path was not imploded')

            # files

            # exist
            for path in [DBDir.path(), FileDir.path()]:
                self.assertTrue(os.path.isdir(path))
