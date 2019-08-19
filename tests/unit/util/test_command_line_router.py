import unittest

from deepstar.util.command_line_route_handler import CommandLineRouteHandler
from deepstar.util.command_line_route_not_found_error import \
    CommandLineRouteNotFoundError
from deepstar.util.command_line_router import CommandLineRouter


class TestCommandLineRouter(unittest.TestCase):
    """
    This class tests the CommandLineRouter class.
    """

    def test_matches_single_route_successfully(self):
        class TestCommandLineRouteHandler(CommandLineRouteHandler):
            def handle(self, args, opts):
                TestCommandLineRouteHandler.flag = True

        argv = ['test0', 'test1', 'test2']

        routes = [
            ('^test1', TestCommandLineRouteHandler)
        ]

        CommandLineRouter().route(routes, argv)

        self.assertTrue(TestCommandLineRouteHandler.flag)

    def test_matches_multiple_routes_successfully_1(self):
        class TestCommandLineRouteHandler(CommandLineRouteHandler):
            def handle(self, args, opts):
                TestCommandLineRouteHandler.flag = True

        argv = ['test0', 'test1', 'test2']

        routes = [
            ('^test1', TestCommandLineRouteHandler),
            ('^test1 test2', None)
        ]

        CommandLineRouter().route(routes, argv)

        self.assertTrue(TestCommandLineRouteHandler.flag)

    def test_matches_multiple_routes_successfully_2(self):
        class TestCommandLineRouteHandler(CommandLineRouteHandler):
            def handle(self, args, opts):
                TestCommandLineRouteHandler.flag = True

        argv = ['test0', 'test1', 'test2']

        routes = [
            ('^test1 test2', TestCommandLineRouteHandler),
            ('^test1', None)
        ]

        CommandLineRouter().route(routes, argv)

        self.assertTrue(TestCommandLineRouteHandler.flag)

    def test_fails_to_match_single_route_and_raises_error(self):
        class TestCommandLineRouteHandler(CommandLineRouteHandler):
            def handle(self, args, opts):
                pass

        argv = ['test0', 'test1', 'test2']

        routes = [
            ('^test3', TestCommandLineRouteHandler)
        ]

        with self.assertRaises(CommandLineRouteNotFoundError):
            CommandLineRouter().route(routes, argv)

    def test_parses_options_successfully(self):
        class TestCommandLineRouteHandler(CommandLineRouteHandler):
            def handle(self, args, opts):
                TestCommandLineRouteHandler.args = args
                TestCommandLineRouteHandler.opts = opts

        argv = ['test0', 'test1', 'test2', '--a', '--b=c', '--def', '--ghi=jkl', '-m', '-n=o', '-pqr', '-stu=vwx']  # noqa

        routes = [
            ('^test1', TestCommandLineRouteHandler)
        ]

        CommandLineRouter().route(routes, argv)

        self.assertEqual(TestCommandLineRouteHandler.args, ['test0', 'test1', 'test2'])  # noqa
        self.assertEqual(TestCommandLineRouteHandler.opts, {'a': True, 'b': 'c', 'def': True, 'ghi': 'jkl', 'm': True, 'n': 'o', 'pqr': True, 'stu': 'vwx'})  # noqa
