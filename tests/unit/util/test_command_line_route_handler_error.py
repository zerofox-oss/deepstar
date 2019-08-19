import unittest

from deepstar.util.command_line_route_handler_error import CommandLineRouteHandlerError  # noqa


class TestCommandLineRouteHandlerError(unittest.TestCase):
    """
    This class tests the CommandLineRouteHandlerError class.
    """

    def test_message(self):
        e = None

        try:
            raise CommandLineRouteHandlerError('test')
        except CommandLineRouteHandlerError as e_:
            e = e_

        self.assertEqual(e.message, 'test')
