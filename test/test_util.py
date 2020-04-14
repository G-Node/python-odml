"""
This file tests odml util functions.
"""

import unittest

from odml.util import format_cardinality


class TestUtil(unittest.TestCase):

    def test_format_cardinality(self):
        # Test empty set
        self.assertIsNone(format_cardinality(None))
        self.assertIsNone(format_cardinality([]))
        self.assertIsNone(format_cardinality({}))
        self.assertIsNone(format_cardinality(""))
        self.assertIsNone(format_cardinality(()))

        # Test empty tuple edge cases
        self.assertIsNone(format_cardinality((None, None)))
        self.assertIsNone(format_cardinality((0, 0)))
        self.assertIsNone(format_cardinality((None, 0)))
        self.assertIsNone(format_cardinality((0, None)))

        # Test single int max set
        self.assertEqual(format_cardinality(10), (None, 10))

        # Test tuple set
        set_val = (2, None)
        self.assertEqual(format_cardinality(set_val), set_val)
        set_val = (None, 2)
        self.assertEqual(format_cardinality(set_val), set_val)
        set_val = (2, 3)
        self.assertEqual(format_cardinality(set_val), set_val)

        # Test set failures
        with self.assertRaises(ValueError):
            format_cardinality("a")

        with self.assertRaises(ValueError):
            format_cardinality(-1)

        with self.assertRaises(ValueError):
            format_cardinality((1, "b"))

        with self.assertRaises(ValueError):
            format_cardinality((1, 2, 3))

        with self.assertRaises(ValueError):
            format_cardinality((-1, 1))

        with self.assertRaises(ValueError):
            format_cardinality((1, -5))

        with self.assertRaises(ValueError) as exc:
            format_cardinality((5, 1))
            self.assertIn("Minimum larger than maximum ", str(exc))
