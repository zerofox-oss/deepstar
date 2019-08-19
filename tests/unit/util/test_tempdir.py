import os
import unittest

from deepstar.util.tempdir import tempdir


class TestTempDir(unittest.TestCase):
    """
    This class tests the tempdir module.
    """

    def test(self):
        t = None

        with tempdir() as tempdir_:
            self.assertTrue(os.path.isdir(tempdir_))

            t = tempdir_

        self.assertFalse(os.path.isdir(t))
