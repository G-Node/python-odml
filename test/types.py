import unittest

import odml.types as typ
import datetime

class TestTypes(unittest.TestCase):
    def test_date(self):
        date = datetime.date(2011, 12, 1)
        date_string = '2011-12-01'
        self.assertEqual(date, typ.date_get(date_string))
        self.assertEqual(typ.date_set(date), date_string)

    def test_time(self):
        time = datetime.time(12,34,56)
        time_string = '12:34:56'
        self.assertEqual(time, typ.time_get(time_string))
        self.assertEqual(typ.time_set(time), time_string)

    def test_datetime(self):
        date = datetime.datetime(2011, 12, 1, 12, 34, 56)
        date_string = '2011-12-01 12:34:56'
        self.assertEqual(date, typ.datetime_get(date_string))
        self.assertEqual(typ.datetime_set(date), date_string)

if __name__ == '__main__':
    unittest.main()
