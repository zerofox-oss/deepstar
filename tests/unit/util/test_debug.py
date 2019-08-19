from io import StringIO
from mock import patch
import os
import sys
import unittest

from deepstar.util.debug import debug


class TestDebug(unittest.TestCase):
    """
    This class tests the debug function.
    """

    def test_debug_level_3(self):
        try:
            sys.stdout = StringIO()
            debug('test', 0)
            self.assertEqual(sys.stdout.getvalue().strip(), 'test')

            sys.stdout = StringIO()
            debug('test', 1)
            self.assertEqual(sys.stdout.getvalue().strip(), 'test')

            sys.stdout = StringIO()
            debug('test', 2)
            self.assertEqual(sys.stdout.getvalue().strip(), 'test')

            sys.stdout = StringIO()
            debug('test', 3)
            self.assertEqual(sys.stdout.getvalue().strip(), 'test')

            sys.stdout = StringIO()
            debug('test', 4)
            self.assertEqual(sys.stdout.getvalue().strip(), '')

            sys.stdout = StringIO()
            debug('test', 5)
            self.assertEqual(sys.stdout.getvalue().strip(), '')
        finally:
            sys.stdout = sys.__stdout__

    def test_debug_level_1(self):
        try:
            with patch.dict(os.environ, {'DEBUG_LEVEL': '1'}):
                sys.stdout = StringIO()
                debug('test', 0)
                self.assertEqual(sys.stdout.getvalue().strip(), 'test')

                sys.stdout = StringIO()
                debug('test', 1)
                self.assertEqual(sys.stdout.getvalue().strip(), 'test')

                sys.stdout = StringIO()
                debug('test', 2)
                self.assertEqual(sys.stdout.getvalue().strip(), '')

                sys.stdout = StringIO()
                debug('test', 3)
                self.assertEqual(sys.stdout.getvalue().strip(), '')

                sys.stdout = StringIO()
                debug('test', 4)
                self.assertEqual(sys.stdout.getvalue().strip(), '')

                sys.stdout = StringIO()
                debug('test', 5)
                self.assertEqual(sys.stdout.getvalue().strip(), '')
        finally:
            sys.stdout = sys.__stdout__
