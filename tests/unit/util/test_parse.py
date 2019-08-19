import unittest

from deepstar.util.parse import parse_range


class TestParse(unittest.TestCase):
    """
    This class tests the parse module.
    """

    def test_parse_range(self):
        self.assertEqual(parse_range('1'), [1])
        self.assertEqual(parse_range('1-3'), [1, 2, 3])
        self.assertEqual(parse_range('1,3'), [1, 3])
        self.assertEqual(parse_range('1-3,5-7'), [1, 2, 3, 5, 6, 7])
        self.assertEqual(parse_range('1-3,5,7-9'), [1, 2, 3, 5, 7, 8, 9])
        self.assertEqual(parse_range('1 - 3'), [1, 2, 3])
        self.assertEqual(parse_range('1 , 3'), [1, 3])
        self.assertEqual(parse_range('1 - 3 , 5 - 7'), [1, 2, 3, 5, 6, 7])
        self.assertEqual(parse_range('1 - 3, 5 , 7 - 9'), [1, 2, 3, 5, 7, 8, 9])  # noqa

    def test_parse_range_fails_to_parse_non_digit(self):
        with self.assertRaises(ValueError):
            parse_range('a')
