import datetime
import unittest

from sys import version_info

import odml.dtypes as typ


class TestTypes(unittest.TestCase):

    def assert_local_regexp(self, text, regular_expression):
        """
        Python 2 is dead and assertRegexpMatches is deprecated and
        will be removed, but keep compatibility until py 2 support is
        fully dropped.
        """

        if version_info.major < 3:
            self.assertRegexpMatches(text, regular_expression)
        else:
            self.assertRegex(text, regular_expression)

    def test_valid_type(self):
        # Test None
        self.assertTrue(typ.valid_type(None))

        # Test that all DTypes classify as valid dtypes.
        for curr_type in typ.DType:
            self.assertTrue(typ.valid_type(curr_type), "Invalid DType %s" % curr_type)

        # Test that provided shorthand dtypes return as valid dtypes.
        for curr_shorthand in typ._dtype_map:
            self.assertTrue(typ.valid_type(curr_shorthand),
                            "Invalid dtype shorthand %s" % curr_shorthand)

        # Test valid tuple dtype
        self.assertTrue(typ.valid_type("2-tuple"))
        self.assertTrue(typ.valid_type("293939-tuple"))

        # Test invalid dtypes
        self.assertFalse(typ.valid_type(1))
        self.assertFalse(typ.valid_type("unsupported"))
        self.assertFalse(typ.valid_type("x-tuple"))

    def test_date(self):
        self.assertIsInstance(typ.date_get(None), datetime.date)
        self.assertIsInstance(typ.date_get(""), datetime.date)

        reg = "^[0-9]{4}-(0[1-9]|1[0-2])-([0-2][0-9]|3[0-1])$"
        self.assert_local_regexp(typ.date_get(None).strftime(typ.FORMAT_DATE), reg)
        self.assert_local_regexp(typ.date_get("").strftime(typ.FORMAT_DATE), reg)

        date = datetime.date(2011, 12, 1)
        date_string = '2011-12-01'
        self.assertEqual(date, typ.date_get(date_string))
        self.assertEqual(date, typ.date_get(date))

        with self.assertRaises(TypeError):
            _ = typ.date_get([])
        with self.assertRaises(TypeError):
            _ = typ.date_get({})
        with self.assertRaises(TypeError):
            _ = typ.date_get(False)

        # Test fail on datetime.datetime
        with self.assertRaises(ValueError):
            _ = typ.date_get(datetime.datetime.now())

        # Test fail on datetime.time
        with self.assertRaises(TypeError):
            _ = typ.date_get(datetime.datetime.now().time())

        # Test fail on invalid string format
        with self.assertRaises(ValueError):
            _ = typ.date_get("11.11.1111")

    def test_time(self):
        self.assertIsInstance(typ.time_get(None), datetime.time)
        self.assertIsInstance(typ.time_get(""), datetime.time)

        reg = "^[0-5][0-9]:[0-5][0-9]:[0-5][0-9]$"
        self.assert_local_regexp(typ.time_get(None).strftime(typ.FORMAT_TIME), reg)
        self.assert_local_regexp(typ.time_get("").strftime(typ.FORMAT_TIME), reg)

        time = datetime.time(12, 34, 56)
        time_string = '12:34:56'
        self.assertEqual(time, typ.time_get(time_string))
        self.assertEqual(time, typ.time_get(time))

        with self.assertRaises(TypeError):
            _ = typ.time_get([])
        with self.assertRaises(TypeError):
            _ = typ.time_get({})
        with self.assertRaises(TypeError):
            _ = typ.time_get(False)

        # Test fail on datetime.datetime
        with self.assertRaises(TypeError):
            _ = typ.time_get(datetime.datetime.now())

        # Test fail on datetime.date
        with self.assertRaises(TypeError):
            _ = typ.time_get(datetime.datetime.now().date())

        # Test fail on invalid string format
        with self.assertRaises(ValueError):
            _ = typ.time_get("11-11-11")

    def test_datetime(self):
        self.assertIsInstance(typ.datetime_get(None), datetime.datetime)
        self.assertIsInstance(typ.datetime_get(""), datetime.datetime)

        reg = "^[0-9]{4}-(0[1-9]|1[0-2])-([0-2][0-9]|3[0-1]) [0-5][0-9]:[0-5][0-9]:[0-5][0-9]$"
        self.assert_local_regexp(typ.datetime_get(None).strftime(typ.FORMAT_DATETIME), reg)
        self.assert_local_regexp(typ.datetime_get("").strftime(typ.FORMAT_DATETIME), reg)

        date = datetime.datetime(2011, 12, 1, 12, 34, 56)
        date_string = '2011-12-01 12:34:56'
        self.assertEqual(date, typ.datetime_get(date_string))
        self.assertEqual(date, typ.datetime_get(date))

        with self.assertRaises(TypeError):
            _ = typ.datetime_get([])
        with self.assertRaises(TypeError):
            _ = typ.datetime_get({})
        with self.assertRaises(TypeError):
            _ = typ.datetime_get(False)

        # Test fail on datetime.time
        with self.assertRaises(TypeError):
            _ = typ.datetime_get(datetime.datetime.now().time())

        # Test fail on datetime.date
        with self.assertRaises(TypeError):
            _ = typ.datetime_get(datetime.datetime.now().date())

        # Test fail on invalid string format
        with self.assertRaises(ValueError):
            _ = typ.datetime_get("11.11.1111 12:12:12")

    def test_int(self):
        self.assertEqual(typ.default_values("int"), typ.int_get(None))
        self.assertEqual(typ.default_values("int"), typ.int_get(""))

        self.assertIsInstance(typ.int_get(11), int)
        self.assertIsInstance(typ.int_get(1.1), int)
        self.assertIsInstance(typ.int_get("11"), int)
        self.assertEqual(typ.int_get("123456789012345678901"), 123456789012345678901)
        self.assertEqual(typ.int_get("-123456789012345678901"), -123456789012345678901)
        self.assertEqual(typ.int_get("123.45"), 123)

        with self.assertRaises(TypeError):
            _ = typ.int_get([])
        with self.assertRaises(TypeError):
            _ = typ.int_get({})
        with self.assertRaises(ValueError):
            _ = typ.int_get("fail")

    def test_float(self):
        self.assertEqual(typ.default_values("float"), typ.float_get(None))
        self.assertEqual(typ.default_values("float"), typ.float_get(""))

        self.assertIsInstance(typ.float_get(1), float)
        self.assertIsInstance(typ.float_get("1.1"), float)
        self.assertEqual(typ.float_get(123.45), 123.45)

        with self.assertRaises(TypeError):
            _ = typ.float_get([])
        with self.assertRaises(TypeError):
            _ = typ.float_get({})
        with self.assertRaises(ValueError):
            _ = typ.float_get("fail")

    def test_str(self):
        self.assertEqual(typ.default_values("string"), typ.str_get(None))
        self.assertEqual(typ.default_values("string"), typ.str_get(""))
        self.assertEqual(typ.default_values("string"), typ.str_get([]))
        self.assertEqual(typ.default_values("string"), typ.str_get({}))

        # Make sure boolean values are properly converted to string.
        self.assertEqual(typ.str_get(False), 'False')
        self.assertEqual(typ.str_get(True), 'True')

    def test_bool(self):
        self.assertEqual(typ.default_values("boolean"), typ.boolean_get(None))
        self.assertEqual(typ.default_values("boolean"), typ.boolean_get(""))
        self.assertEqual(typ.default_values("boolean"), typ.boolean_get([]))
        self.assertEqual(typ.default_values("boolean"), typ.boolean_get({}))

        true_values = [True, "TRUE", "true", "T", "t", "1", 1]
        for val in true_values:
            self.assertTrue(typ.boolean_get(val))

        false_values = [False, "FALSE", "false", "F", "f", "0", 0]
        for val in false_values:
            self.assertFalse(typ.boolean_get(val))

        with self.assertRaises(ValueError):
            typ.boolean_get("text")
        with self.assertRaises(ValueError):
            typ.boolean_get(12)
        with self.assertRaises(ValueError):
            typ.boolean_get(2.1)

    def test_tuple(self):
        self.assertIs(typ.tuple_get(""), None)
        self.assertIs(typ.tuple_get(None), None)

        self.assertEqual(typ.tuple_get("(39.12; 67.19)"), ["39.12", "67.19"])

        # Test fail on missing parenthesis.
        with self.assertRaises(ValueError):
            _ = typ.tuple_get("fail")
        # Test fail on mismatching element count and count number.
        with self.assertRaises(ValueError):
            _ = typ.tuple_get("(1; 2; 3)", 2)

    def test_dtype_none(self):
        self.assertEqual(typ.get({'name': 'Marie'}), "{'name': 'Marie'}")
