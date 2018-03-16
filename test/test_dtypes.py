import unittest

import odml.dtypes as typ
import odml
import datetime


class TestTypes(unittest.TestCase):

    def setUp(self):
        pass

    def test_date(self):
        self.assertIsInstance(typ.date_get(None), datetime.date)
        self.assertIsInstance(typ.date_get(""), datetime.date)

        re = "^[0-9]{4}-(0[1-9]|1[0-2])-([0-2][0-9]|3[0-1])$"
        self.assertRegexpMatches(typ.date_get(None).strftime(typ.FORMAT_DATE), re)
        self.assertRegexpMatches(typ.date_get("").strftime(typ.FORMAT_DATE), re)

        date = datetime.date(2011, 12, 1)
        date_string = '2011-12-01'
        self.assertEqual(date, typ.date_get(date_string))
        self.assertEqual(date, typ.date_get(date))

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

        re = "^[0-5][0-9]:[0-5][0-9]:[0-5][0-9]$"
        self.assertRegexpMatches(typ.time_get(None).strftime(typ.FORMAT_TIME), re)
        self.assertRegexpMatches(typ.time_get("").strftime(typ.FORMAT_TIME), re)

        time = datetime.time(12, 34, 56)
        time_string = '12:34:56'
        self.assertEqual(time, typ.time_get(time_string))
        self.assertEqual(time, typ.time_get(time))

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

        re = "^[0-9]{4}-(0[1-9]|1[0-2])-([0-2][0-9]|3[0-1]) " \
             "[0-5][0-9]:[0-5][0-9]:[0-5][0-9]$"
        self.assertRegexpMatches(typ.datetime_get(None).strftime(typ.FORMAT_DATETIME), re)
        self.assertRegexpMatches(typ.datetime_get("").strftime(typ.FORMAT_DATETIME), re)

        date = datetime.datetime(2011, 12, 1, 12, 34, 56)
        date_string = '2011-12-01 12:34:56'
        self.assertEqual(date, typ.datetime_get(date_string))
        self.assertEqual(date, typ.datetime_get(date))

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

        p = odml.Property("test", value="123456789012345678901", dtype="int")
        self.assertEqual(p.value[0], 123456789012345678901)
        p = odml.Property("test", value="-123456789012345678901", dtype="int")
        self.assertEqual(p.value[0], -123456789012345678901)
        p = odml.Property("test", value="123.45", dtype="int")
        self.assertEqual(p.value[0], 123)

    def test_str(self):
        self.assertEqual(typ.default_values("string"), typ.str_get(None))
        self.assertEqual(typ.default_values("string"), typ.str_get(""))

        s = odml.Property(name='Name', value='Sherin')
        self.assertEqual(s.value[0], 'Sherin')
        self.assertEqual(s.dtype, 'string')

        s.value = 'Jerin'
        self.assertEqual(s.value[0], 'Jerin')
        self.assertEqual(s.dtype, 'string')

    def test_bool(self):
        self.assertEqual(typ.default_values("boolean"), typ.boolean_get(None))
        self.assertEqual(typ.default_values("boolean"), typ.boolean_get(""))

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
        # Success test
        t = odml.Property(name="Location", value='(39.12; 67.19)', dtype='2-tuple')
        tuple_value = t.value[0]  # As the formed tuple is a list of list
        self.assertEqual(tuple_value[0], '39.12')
        self.assertEqual(tuple_value[1], '67.19')

        # Failure test. More tuple values then specified.
        with self.assertRaises(ValueError):
            t = odml.Property(name="Public-Key", value='(5689; 1254; 687)',
                              dtype='2-tuple')

    def test_dtype_none(self):
        t = odml.Property(name="Record", value={'name': 'Marie'})
        self.assertEqual(t.dtype, 'string')
        self.assertEqual(t.value[0], "{'name': 'Marie'}")
