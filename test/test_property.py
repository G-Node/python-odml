import unittest
import datetime

from odml import Property, Section, Document, DType
from odml.property import BaseProperty
from odml.section import BaseSection


class TestProperty(unittest.TestCase):

    def test_simple_attributes(self):
        p_name = "propertyName"
        p_origin = "from over there"
        p_unit = "pears"
        p_uncertainty = "12"
        p_ref = "4 8 15 16 23"
        p_def = "an odml test property"
        p_dep = "yes"
        p_dep_val = "42"

        prop = Property(name=p_name, value_origin=p_origin, unit=p_unit,
                        uncertainty=p_uncertainty, reference=p_ref, definition=p_def,
                        dependency=p_dep, dependency_value=p_dep_val)

        self.assertEqual(prop.name, p_name)
        self.assertEqual(prop.value_origin, p_origin)
        self.assertEqual(prop.unit, p_unit)
        self.assertEqual(prop.uncertainty, p_uncertainty)
        self.assertEqual(prop.reference, p_ref)
        self.assertEqual(prop.definition, p_def)
        self.assertEqual(prop.dependency, p_dep)
        self.assertEqual(prop.dependency_value, p_dep_val)

        # Test setting attributes
        prop.name = "%s_edit" % p_name
        self.assertEqual(prop.name, "%s_edit" % p_name)
        prop.value_origin = "%s_edit" % p_origin
        self.assertEqual(prop.value_origin, "%s_edit" % p_origin)
        prop.unit = "%s_edit" % p_unit
        self.assertEqual(prop.unit, "%s_edit" % p_unit)
        prop.uncertainty = 13
        self.assertEqual(prop.uncertainty, 13.0)
        prop.reference = "%s_edit" % p_ref
        self.assertEqual(prop.reference, "%s_edit" % p_ref)
        prop.definition = "%s_edit" % p_def
        self.assertEqual(prop.definition, "%s_edit" % p_def)
        prop.dependency = "%s_edit" % p_dep
        self.assertEqual(prop.dependency, "%s_edit" % p_dep)
        prop.dependency_value = "%s_edit" % p_dep_val
        self.assertEqual(prop.dependency_value, "%s_edit" % p_dep_val)

        # Test setting attributes to None when '' is passed.
        prop.value_origin = ""
        self.assertIsNone(prop.value_origin)
        prop.unit = ""
        self.assertIsNone(prop.unit)
        prop.uncertainty = ""
        self.assertIsNone(prop.uncertainty)
        prop.reference = ""
        self.assertIsNone(prop.reference)
        prop.definition = ""
        self.assertIsNone(prop.definition)
        prop.dependency = ""
        self.assertIsNone(prop.dependency)
        prop.dependency_value = ""
        self.assertIsNone(prop.dependency_value)

    def test_value(self):
        prop = Property("property", 100)
        self.assertEqual(prop.values[0], 100)
        self.assertIsInstance(prop.values, list)

        prop.values = None
        self.assertEqual(len(prop), 0)

        prop.values = [1, 2, 3]
        prop.values = ""
        self.assertEqual(len(prop), 0)

        prop.values = [1, 2, 3]
        prop.values = []
        self.assertEqual(len(prop), 0)

        prop.values = [1, 2, 3]
        prop.values = ()
        self.assertEqual(len(prop), 0)

        prop.values.append(5)
        self.assertEqual(len(prop.values), 0)

        prop2 = Property("test", {"name": "Marie"})
        self.assertEqual(len(prop2), 1)

        # Test tuple dtype value.
        prop_tuple = Property(name="Location", value='(39.12; 67.19)', dtype='2-tuple')
        tuple_value = prop_tuple.values[0]  # As the formed tuple is a list of list
        self.assertEqual(tuple_value[0], '39.12')
        self.assertEqual(tuple_value[1], '67.19')

        # Test invalid tuple length
        with self.assertRaises(ValueError):
            _ = Property(name="Public-Key", value='(5689; 1254; 687)', dtype='2-tuple')

        prop3 = Property('myprop', value=0, dtype=DType.int)
        self.assertEqual(prop3.value, [0])
        self.assertEqual(prop3.values, [0])

        prop4 = Property('myprop', value=0, dtype=DType.boolean)
        self.assertEqual(prop4.value, [False])
        self.assertEqual(prop4.values, [False])

        prop5 = Property('myprop', value=0)
        self.assertEqual(prop5.value, [0])
        self.assertEqual(prop5.values, [0])

        with self.assertRaises(ValueError):
            Property(name="dateprop", dtype=DType.date, value=['20190707'])

        with self.assertRaises(ValueError):
            Property(name="timeprop", dtype=DType.time, value=['11.11.11'])

        with self.assertRaises(ValueError):
            Property(name="datetimeprop", dtype=DType.datetime, value=['20190707'])

        with self.assertRaises(ValueError):
            Property(name="intprop", dtype=DType.int, value=[2, "Hello!", 4])

        prop6 = Property('myprop', values=["(8; 9; 10)", "(11; 12; 13)"], dtype="3-tuple")
        self.assertEqual(len(prop6.values), 2)

        prop7 = Property('myprop', values=[["0", "1", "2"], [3, 4, 5]], dtype="3-tuple")
        self.assertEqual(len(prop7.values), 2)

        prop8 = Property('myprop', values=["(8; 9; 10)", ["0", "1", "2"], [3, 4, 5]], dtype="3-tuple")
        self.assertEqual(len(prop8.values), 3)


    def test_value_append(self):
        # Test append w/o Property value or dtype
        prop = Property(name="append")
        prop.append(1)
        self.assertEqual(prop.dtype, DType.int)
        self.assertEqual(prop.values, [1])

        # Test append with Property dtype.
        prop = Property(name="append", dtype="int")
        prop.append(3)
        self.assertEqual(prop.values, [3])

        # Test append with Property value
        prop = Property(name="append", value=[1, 2])
        prop.append(3)
        self.assertEqual(prop.values, [1, 2, 3])

        # Test append with Property list value
        prop = Property(name="append", value=[1, 2])
        prop.append([3])
        self.assertEqual(prop.values, [1, 2, 3])

        # Test append of empty values, make sure 0 and False are properly handled
        prop = Property(name="append")
        prop.append(None)
        prop.append("")
        prop.append([])
        prop.append({})
        self.assertEqual(prop.values, [])

        prop.append(0)
        self.assertEqual(prop.values, [0])

        prop.values = None
        prop.dtype = None
        prop.append(False)
        self.assertEqual(prop.values, [False])

        prop = Property(name="append", value=[1, 2])
        prop.append(None)
        prop.append("")
        prop.append([])
        prop.append({})
        self.assertEqual(prop.values, [1, 2])

        prop.append(0)
        self.assertEqual(prop.values, [1, 2, 0])

        # Test fail append with multiple values
        prop = Property(name="append", value=[1, 2, 3])
        with self.assertRaises(ValueError):
            prop.append([4, 5])
        self.assertEqual(prop.values, [1, 2, 3])

        # Test fail append with mismatching dtype
        prop = Property(name="append", value=[1, 2], dtype="int")
        with self.assertRaises(ValueError):
            prop.append([3.14])
        with self.assertRaises(ValueError):
            prop.append([True])
        with self.assertRaises(ValueError):
            prop.append(["5.927"])
        self.assertEqual(prop.values, [1, 2])

        # Test strict flag
        prop.append(3.14, strict=False)
        prop.append(True, strict=False)
        prop.append("5.927", strict=False)
        self.assertEqual(prop.values, [1, 2, 3, 1, 5])

        # Make sure non-convertible values still raise an error
        with self.assertRaises(ValueError):
            prop.append("invalid")
        self.assertEqual(prop.values, [1, 2, 3, 1, 5])

        prop5 = Property("test", value="a string")
        prop5.append("Freude")
        self.assertEqual(len(prop5), 2)
        self.assertRaises(ValueError, prop5.append, "[a, b, c]")

        prop6 = Property(name="prop", value=["A Abraham", "B Barnes", "C Clark"],
                         dtype=DType.person)
        prop6.append("D Dickins")
        self.assertEqual(len(prop6), 4)
        self.assertRaises(ValueError, prop6.append, 1)
        self.assertRaises(ValueError, prop6.append, 1.3)
        self.assertRaises(ValueError, prop6.append, True)

        prop7 = Property(name="prop", value=["https://en.wikipedia.org/wiki/Earth"],
                         dtype=DType.url)
        prop7.append("https://en.wikipedia.org/wiki/Mars")
        self.assertEqual(len(prop7), 2)
        self.assertRaises(ValueError, prop7.append, 1)
        self.assertRaises(ValueError, prop7.append, 1.3)
        self.assertRaises(ValueError, prop7.append, True)

        prop8 = Property(name="prop", value=["Earth is No. 3."], dtype=DType.text)
        prop8.append("Mars is No. 4.")
        self.assertEqual(len(prop8), 2)
        self.assertRaises(ValueError, prop8.append, 1)
        self.assertRaises(ValueError, prop8.append, 1.3)
        self.assertRaises(ValueError, prop8.append, True)

        prop9 = Property(name="tuple-test", dtype="3-tuple", values="(1; 2; 3)")
        prop9.append("(7; 8; 9)")
        self.assertEqual(len(prop9), 2)
        self.assertRaises(ValueError, prop9.append, "(10; 11)")
        prop9.append([[2, 3, 4]])
        self.assertEqual(len(prop9), 3)
        self.assertRaises(ValueError, prop9.append, [[10, 11]])

        prop10 = Property(name="prop10", dtype="date", values=['2011-12-01', '2011-12-02'])
        with self.assertRaises(ValueError):
            prop10.append('2011-12-03', strict=True)
        self.assertEqual(prop10.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 2)])
        prop10.append('2011-12-03', strict=False)
        self.assertEqual(prop10.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 2),
                                         datetime.date(2011, 12, 3)])
        prop10.append([datetime.date(2011, 12, 4)], strict=True)
        self.assertEqual(prop10.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 2),
                                         datetime.date(2011, 12, 3), datetime.date(2011, 12, 4)])


        prop11 = Property(name="prop11", dtype="time", values=['12:00:01', '12:00:02'])
        with self.assertRaises(ValueError):
            prop11.append('12:00:03', strict=True)
        self.assertEqual(prop11.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 2)])
        prop11.append('12:00:03', strict=False)
        self.assertEqual(prop11.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 2),
                                         datetime.time(12, 0, 3)])
        prop11.append([datetime.time(12, 0, 4)], strict=True)
        self.assertEqual(prop11.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 2),
                                         datetime.time(12, 0, 3), datetime.time(12, 0, 4)])

        prop12 = Property(name="prop12", dtype="datetime",
                          values=['2011-12-01 12:00:01', '2011-12-01 12:00:02'])
        with self.assertRaises(ValueError):
            prop12.append('2011-12-01 12:00:03', strict=True)
        self.assertEqual(prop12.values, [datetime.datetime(2011, 12, 1, 12, 0, 1),
                                         datetime.datetime(2011, 12, 1, 12, 0, 2)])
        prop12.append('2011-12-01 12:00:03', strict=False)
        self.assertEqual(prop12.values, [datetime.datetime(2011, 12, 1, 12, 0, 1),
                                         datetime.datetime(2011, 12, 1, 12, 0, 2),
                                         datetime.datetime(2011, 12, 1, 12, 0, 3)])
        prop12.append([datetime.datetime(2011, 12, 1, 12, 0, 4)], strict=True)
        self.assertEqual(prop12.values, [datetime.datetime(2011, 12, 1, 12, 0, 1),
                                         datetime.datetime(2011, 12, 1, 12, 0, 2),
                                         datetime.datetime(2011, 12, 1, 12, 0, 3),
                                         datetime.datetime(2011, 12, 1, 12, 0, 4)])

    def test_value_extend(self):
        prop = Property(name="extend")

        # Test extend w/o Property value or dtype.
        val = [1, 2, 3]
        prop.extend(val)
        self.assertEqual(prop.dtype, DType.int)
        self.assertEqual(prop.values, val)

        # Extend with single value.
        prop.extend(4)
        self.assertEqual(prop.values, [1, 2, 3, 4])

        # Extend with list value.
        prop.extend([5, 6])
        self.assertEqual(prop.values, [1, 2, 3, 4, 5, 6])

        # Test extend w/o Property value
        prop = Property(name="extend", dtype="float")
        prop.extend([1.0, 2.0, 3.0])
        self.assertEqual(prop.values, [1.0, 2.0, 3.0])

        # Test extend with Property value
        prop = Property(name="extend", value=10)
        prop.extend([20, 30, '40'])
        self.assertEqual(prop.values, [10, 20, 30, 40])

        # Test extend fail with mismatching dtype
        with self.assertRaises(ValueError):
            prop.extend(['5', 6, 7])
        with self.assertRaises(ValueError):
            prop.extend([5, 6, 'a'])

        # Test extend via Property
        prop = Property(name="extend", value=["a", "b"])
        ext_prop = Property(name="value extend", value="c")
        prop.extend(ext_prop)
        self.assertEqual(prop.values, ["a", "b", "c"])

        ext_prop.values = ["d", "e"]
        prop.extend(ext_prop)
        self.assertEqual(prop.values, ["a", "b", "c", "d", "e"])

        ext_prop = Property(name="value extend", value=[1, 2, 3])
        with self.assertRaises(ValueError):
            prop.extend(ext_prop)
        self.assertEqual(prop.values, ["a", "b", "c", "d", "e"])

        # Test extend via Property unit check
        prop = Property(name="extend", value=[1, 2], unit="mV")
        ext_prop = Property(name="extend", value=[3, 4], unit="mV")
        prop.extend(ext_prop)
        self.assertEqual(prop.values, [1, 2, 3, 4])

        ext_prop.unit = "kV"
        with self.assertRaises(ValueError):
            prop.extend(ext_prop)
        self.assertEqual(prop.values, [1, 2, 3, 4])

        ext_prop.unit = ""
        with self.assertRaises(ValueError):
            prop.extend(ext_prop)
        self.assertEqual(prop.values, [1, 2, 3, 4])

        # Test strict flag
        prop = Property(name="extend", value=[1, 2], dtype="int")
        with self.assertRaises(ValueError):
            prop.extend([3.14, True, "5.927"])
        self.assertEqual(prop.values, [1, 2])

        prop.extend([3.14, True, "5.927"], strict=False)
        self.assertEqual(prop.values, [1, 2, 3, 1, 5])

        # Make sure non-convertible values still raise an error
        with self.assertRaises(ValueError):
            prop.extend([6, "some text"])

        prop1 = Property(name="prop", value=["A Abraham", "B Barnes", "C Clark"],
                         dtype=DType.person)
        prop1.extend("D Dickins")
        self.assertEqual(len(prop1), 4)
        self.assertRaises(ValueError, prop1.extend, 1)
        self.assertRaises(ValueError, prop1.extend, 1.3)
        self.assertRaises(ValueError, prop1.extend, True)

        prop2 = Property(name="prop", value=["https://en.wikipedia.org/wiki/Earth"],
                         dtype=DType.url)
        prop2.extend("https://en.wikipedia.org/wiki/Mars")
        self.assertEqual(len(prop2), 2)
        self.assertRaises(ValueError, prop2.extend, 1)
        self.assertRaises(ValueError, prop2.extend, 1.3)
        self.assertRaises(ValueError, prop2.extend, True)

        prop3 = Property(name="prop", value=["Earth is No. 3."], dtype=DType.text)
        prop3.extend("Mars is No. 4.")
        self.assertEqual(len(prop3), 2)
        self.assertRaises(ValueError, prop3.extend, 1)
        self.assertRaises(ValueError, prop3.extend, 1.3)
        self.assertRaises(ValueError, prop3.extend, True)

        prop4 = Property(name="tuple-test", dtype="3-tuple", values="(1; 2; 3)")
        prop4.extend(["(7; 8; 9)", "(10; 11; 12)"])
        self.assertEqual(len(prop4), 3)
        self.assertRaises(ValueError, prop4.extend, "(10; 11)")
        prop4.extend([[2, 3, 4], [5, 6, 7]])
        self.assertEqual(len(prop4), 5)
        self.assertRaises(ValueError, prop4.extend, [[10, 11]])

        prop4 = Property(name="prop4", dtype="date", values=['2011-12-01', '2011-12-02'])
        with self.assertRaises(ValueError):
            prop4.extend('2011-12-03', strict=True)
        self.assertEqual(prop4.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 2)])
        prop4.extend('2011-12-03', strict=False)
        self.assertEqual(prop4.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 2),
                                        datetime.date(2011, 12, 3)])
        prop4.extend([datetime.date(2011, 12, 4)], strict=True)
        self.assertEqual(prop4.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 2),
                                        datetime.date(2011, 12, 3), datetime.date(2011, 12, 4)])
        prop4.extend([datetime.date(2011, 12, 5), datetime.date(2011, 12, 6)], strict=True)
        self.assertEqual(prop4.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 2),
                                        datetime.date(2011, 12, 3), datetime.date(2011, 12, 4),
                                        datetime.date(2011, 12, 5), datetime.date(2011, 12, 6)])
        with self.assertRaises(ValueError):
            prop4.extend(['2011-12-03', 'abc'], strict=False)


        prop5 = Property(name="prop5", dtype="time", values=['12:00:01', '12:00:02'])
        with self.assertRaises(ValueError):
            prop5.extend('12:00:03', strict=True)
        self.assertEqual(prop5.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 2)])
        prop5.extend('12:00:03', strict=False)
        self.assertEqual(prop5.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 2),
                                        datetime.time(12, 0, 3)])
        prop5.extend([datetime.time(12, 0, 4)], strict=True)
        self.assertEqual(prop5.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 2),
                                        datetime.time(12, 0, 3), datetime.time(12, 0, 4)])
        prop5.extend([datetime.time(12, 0, 5), datetime.time(12, 0, 6)], strict=True)
        self.assertEqual(prop5.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 2),
                                        datetime.time(12, 0, 3), datetime.time(12, 0, 4),
                                        datetime.time(12, 0, 5), datetime.time(12, 0, 6)])
        with self.assertRaises(ValueError):
            prop4.extend(['12:00:07', 'abc'], strict=False)

        prop6 = Property(name="prop6", dtype="datetime",
                         values=['2011-12-01 12:00:01', '2011-12-01 12:00:02'])
        with self.assertRaises(ValueError):
            prop6.extend('2011-12-01 12:00:03', strict=True)
        self.assertEqual(prop6.values, [datetime.datetime(2011, 12, 1, 12, 0, 1),
                                        datetime.datetime(2011, 12, 1, 12, 0, 2)])
        prop6.extend('2011-12-01 12:00:03', strict=False)
        self.assertEqual(prop6.values, [datetime.datetime(2011, 12, 1, 12, 0, 1),
                                        datetime.datetime(2011, 12, 1, 12, 0, 2),
                                        datetime.datetime(2011, 12, 1, 12, 0, 3)])
        prop6.extend([datetime.datetime(2011, 12, 1, 12, 0, 4)], strict=True)
        self.assertEqual(prop6.values, [datetime.datetime(2011, 12, 1, 12, 0, 1),
                                        datetime.datetime(2011, 12, 1, 12, 0, 2),
                                        datetime.datetime(2011, 12, 1, 12, 0, 3),
                                        datetime.datetime(2011, 12, 1, 12, 0, 4)])
        prop6.extend([datetime.datetime(2011, 12, 1, 12, 0, 5),
                      datetime.datetime(2011, 12, 1, 12, 0, 6)], strict=True)
        self.assertEqual(prop6.values, [datetime.datetime(2011, 12, 1, 12, 0, 1),
                                        datetime.datetime(2011, 12, 1, 12, 0, 2),
                                        datetime.datetime(2011, 12, 1, 12, 0, 3),
                                        datetime.datetime(2011, 12, 1, 12, 0, 4),
                                        datetime.datetime(2011, 12, 1, 12, 0, 5),
                                        datetime.datetime(2011, 12, 1, 12, 0, 6)])
        with self.assertRaises(ValueError):
            prop4.extend(['2011-12-03 12:00:07', 'abc'], strict=False)

    def test_insert(self):
        prop1 = Property(name="prop1", dtype="int", values=[0,2])
        prop1.insert(1, 1)
        self.assertEqual(prop1.values, [0, 1, 2])
        prop1.insert(4, 3)
        self.assertEqual(prop1.values, [0, 1, 2, 3])

        with self.assertRaises(ValueError):
            prop1.append([4, 5])
        self.assertEqual(prop1.values, [0, 1, 2, 3])

        with self.assertRaises(ValueError):
            prop1.insert(1, 3.14)
        with self.assertRaises(ValueError):
            prop1.insert(1, True)
        with self.assertRaises(ValueError):
            prop1.insert(1, "5.927")
        self.assertEqual(prop1.values, [0, 1, 2, 3])

        prop2 = Property(name="prop2", dtype="int", values=[1, 2])
        prop2.insert(1, 3.14, strict=False)
        self.assertEqual(prop2.values, [1, 3, 2])
        prop2.insert(1, True, strict=False)
        self.assertEqual(prop2.values, [1, 1, 3, 2])
        prop2.insert(1, "5.927", strict=False)
        self.assertEqual(prop2.values, [1, 5, 1, 3, 2])
    
        prop3 = Property(name="prop3", dtype="string", values=["a", "c"])
        prop3.insert(1, "b")
        self.assertEqual(prop3.values, ["a", "b", "c"])
        prop3.insert(1, 1, strict=False)
        self.assertEqual(prop3.values, ["a", "1", "b", "c"])
        with self.assertRaises(ValueError):
            prop3.insert(1, 2, strict=True)
        self.assertEqual(prop3.values, ["a", "1", "b", "c"])

        prop4 = Property(name="prop4", dtype="float", values=[1.1, 1.3])
        prop4.insert(1, 1.2)
        self.assertEqual(prop4.values, [1.1, 1.2, 1.3])
        prop4.insert(1, 2, strict=False)
        self.assertEqual(prop4.values, [1.1, 2.0, 1.2, 1.3])
        with self.assertRaises(ValueError):
            prop4.insert(1, 2, strict=True)
        self.assertEqual(prop4.values, [1.1, 2.0, 1.2, 1.3])
    
        prop5 = Property(name="prop5", dtype="2-tuple", values=["(1; 2)", "(5; 6)"])
        prop5.insert(1, "(3; 4)", strict=True)
        self.assertEqual(prop5.values, [['1', '2'], ['3', '4'], ['5', '6']])
        prop5.insert(1, [['4', '5']], strict=True)
        self.assertEqual(prop5.values, [['1', '2'], ['4', '5'], ['3', '4'], ['5', '6']])
        
        prop6 = Property(name="prop6", dtype="boolean", values=[True, True])
        prop6.insert(1, False)
        self.assertEqual(prop6.values, [True, False, True])
        prop6.insert(1, 1, strict=False)
        self.assertEqual(prop6.values, [True, True, False, True])
        with self.assertRaises(ValueError):
            prop6.insert(1, 2, strict=False)
        self.assertEqual(prop6.values, [True, True, False, True])
        with self.assertRaises(ValueError):
            prop6.insert(1, 0, strict=True)
        self.assertEqual(prop6.values, [True, True, False, True])

        prop7 = Property(name="prop7", dtype="date", values=['2011-12-01', '2011-12-04'])
        with self.assertRaises(ValueError):
            prop7.insert(1, '2011-12-03', strict=True)
        self.assertEqual(prop7.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 4)])
        prop7.insert(1, '2011-12-03', strict=False)
        self.assertEqual(prop7.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 3),
                                        datetime.date(2011, 12, 4)])
        prop7.insert(1, [datetime.date(2011, 12, 2)], strict=True)
        self.assertEqual(prop7.values, [datetime.date(2011, 12, 1), datetime.date(2011, 12, 2),
                                        datetime.date(2011, 12, 3), datetime.date(2011, 12, 4)])


        prop8 = Property(name="prop8", dtype="time", values=['12:00:01', '12:00:04'])
        with self.assertRaises(ValueError):
            prop8.insert(1, '12:00:03', strict=True)
        self.assertEqual(prop8.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 4)])
        prop8.insert(1, '12:00:03', strict=False)
        self.assertEqual(prop8.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 3),
                                        datetime.time(12, 0, 4)])
        prop8.insert(1, [datetime.time(12, 0, 2)], strict=True)
        self.assertEqual(prop8.values, [datetime.time(12, 0, 1), datetime.time(12, 0, 2),
                                        datetime.time(12, 0, 3), datetime.time(12, 0, 4)])

        prop9 = Property(name="prop9", dtype="datetime",
                         values=['2011-12-01 12:00:01', '2011-12-01 12:00:04'])
        with self.assertRaises(ValueError):
            prop9.insert(1, '2011-12-01 12:00:03', strict=True)
        self.assertEqual(prop9.values, [datetime.datetime(2011, 12, 1, 12, 0, 1), 
                                        datetime.datetime(2011, 12, 1, 12, 0, 4)])
        prop9.insert(1, '2011-12-01 12:00:03', strict=False)
        self.assertEqual(prop9.values, [datetime.datetime(2011, 12, 1, 12, 0, 1), 
                                        datetime.datetime(2011, 12, 1, 12, 0, 3),
                                        datetime.datetime(2011, 12, 1, 12, 0, 4)])
        prop9.insert(1, [datetime.datetime(2011, 12, 1, 12, 0, 2)], strict=True)
        self.assertEqual(prop9.values, [datetime.datetime(2011, 12, 1, 12, 0, 1), 
                                        datetime.datetime(2011, 12, 1, 12, 0, 2),
                                        datetime.datetime(2011, 12, 1, 12, 0, 3), 
                                        datetime.datetime(2011, 12, 1, 12, 0, 4)])
        
        prop10 = Property(name="prop", value=["Earth is\n No. 3."], dtype=DType.text)
        prop10.insert(1, "Mars is\n No. 4.", strict=False)
        self.assertEqual(len(prop10), 2)
        self.assertEqual(prop10.values, ["Earth is\n No. 3.", "Mars is\n No. 4."])
        prop10.insert(1, 'A new world emerged?', strict=True)
        self.assertEqual(prop10.values, ["Earth is\n No. 3.",
                                         "A new world emerged?",
                                         "Mars is\n No. 4."])
        prop10.insert(1, 1, strict=False)
        self.assertEqual(prop10.values, ["Earth is\n No. 3.", "1",
                                         "A new world emerged?",
                                         "Mars is\n No. 4."])
        with self.assertRaises(ValueError):
            prop10.insert(1, 1, strict=True)
        self.assertEqual(prop10.values, ["Earth is\n No. 3.", "1",
                                         "A new world emerged?",
                                         "Mars is\n No. 4."])

    def test_reorder(self):
        sec = Section()
        prop_zero = Property(name="prop_zero", parent=sec)
        prop_one = Property(name="prop_one", parent=sec)
        prop_two = Property(name="prop_two", parent=sec)
        prop_three = Property(name="prop_three", parent=sec)

        self.assertEqual(sec.properties[0].name, prop_zero.name)
        self.assertEqual(sec.properties[2].name, prop_two.name)
        prop_two.reorder(0)

        self.assertEqual(sec.properties[0].name, prop_two.name)
        self.assertEqual(sec.properties[1].name, prop_zero.name)
        self.assertEqual(sec.properties[2].name, prop_one.name)
        self.assertEqual(sec.properties[3].name, prop_three.name)

        prop_two.reorder(2)

        self.assertEqual(sec.properties[0].name, prop_zero.name)
        self.assertEqual(sec.properties[1].name, prop_one.name)
        self.assertEqual(sec.properties[2].name, prop_two.name)
        self.assertEqual(sec.properties[3].name, prop_three.name)

        # Test Exception on unconnected property
        prop = Property(name="main")
        with self.assertRaises(ValueError):
            prop.reorder(0)

    def test_get_set_value(self):
        values = [1, 2, 3, 4, 5]
        prop = Property("property", value=values)

        self.assertEqual(len(prop), 5)
        for lval, pval in zip(values, prop.values):
            self.assertEqual(lval, pval)

        count = 0
        for _ in prop:
            count += 1
        self.assertEqual(count, len(values))

        prop[0] = 10
        self.assertEqual(prop[0], 10)
        with self.assertRaises(ValueError):
            prop[1] = 'stringval'

    def test_bool_conversion(self):
        # Success tests
        prop = Property(name='received', value=[1, 0, 1, 0, 1])
        self.assertEqual(prop.dtype, 'int')
        prop.dtype = DType.boolean
        self.assertEqual(prop.dtype, 'boolean')
        self.assertEqual(prop.values, [True, False, True, False, True])

        prop = Property(name='sent', value=['False', True, 'TRUE', '0', 't', 'F', '1'])
        self.assertEqual(prop.dtype, 'string')
        prop.dtype = DType.boolean
        self.assertEqual(prop.dtype, 'boolean')
        self.assertEqual(prop.values, [False, True, True, False, True, False, True])

        # Failure tests
        curr_val = [3, 0, 1, 0, 8]
        curr_type = 'int'
        prop = Property(name='received', value=curr_val)
        self.assertEqual(prop.dtype, curr_type)
        with self.assertRaises(ValueError):
            prop.dtype = DType.boolean
        self.assertEqual(prop.dtype, curr_type)
        self.assertEqual(prop.values, curr_val)

        curr_type = 'string'
        prop = Property(name='sent', value=['False', True, 'TRUE', '0', 't', '12', 'Ft'])
        self.assertEqual(prop.dtype, curr_type)
        with self.assertRaises(ValueError):
            prop.dtype = DType.boolean
        self.assertEqual(prop.dtype, curr_type)

    def test_str_to_int_convert(self):
        # Success Test
        prop = Property(name='cats_onboard', value=['3', '0', '1', '0', '8'])
        self.assertEqual(prop.dtype, 'string')
        prop.dtype = DType.int
        self.assertEqual(prop.dtype, 'int')
        self.assertEqual(prop.values, [3, 0, 1, 0, 8])

        # Failure Test
        prop = Property(name='dogs_onboard', value=['7', '20', '1 Dog', 'Seven'])
        self.assertEqual(prop.dtype, 'string')

        with self.assertRaises(ValueError):
            prop.dtype = DType.int

        self.assertEqual(prop.dtype, 'string')
        self.assertEqual(prop.values, ['7', '20', '1 Dog', 'Seven'])

    def test_name(self):
        # Test id is used when name is not provided
        prop = Property()
        self.assertIsNotNone(prop.name)
        self.assertEqual(prop.name, prop.id)

        # Test name is properly set on init
        name = "rumpelstilzchen"
        prop = Property(name)
        self.assertEqual(prop.name, name)

        # Test name can be properly set on single and connected Properties
        prop = Property()
        self.assertNotEqual(prop.name, "prop")
        prop.name = "prop"
        self.assertEqual(prop.name, "prop")

        sec = Section()
        prop_a = Property(parent=sec)
        self.assertNotEqual(prop_a.name, "prop_a")
        prop_a.name = "prop_a"
        self.assertEqual(prop_a.name, "prop_a")

        # Test property name can be changed with siblings
        prop_b = Property(name="prop_b", parent=sec)
        self.assertEqual(prop_b.name, "prop_b")
        prop_b.name = "prop"
        self.assertEqual(prop_b.name, "prop")

        # Test property name set will fail on existing sibling with same name
        with self.assertRaises(KeyError):
            prop_b.name = "prop_a"
        self.assertEqual(prop_b.name, "prop")

    def test_parent(self):
        prop = Property("property_section", parent=Section("S"))
        self.assertIsInstance(prop.parent, BaseSection)
        self.assertEqual(len(prop.parent.props), 1)

        """ Test if child is removed from _props of a parent after assigning
            a new parent to the child """
        prop_parent = prop.parent
        prop.parent = Section("S1")
        self.assertEqual(len(prop_parent.props), 0)
        self.assertIsInstance(prop.parent, BaseSection)
        self.assertIsInstance(prop.parent.props[0], BaseProperty)

        prop_parent = prop.parent
        prop.parent = None
        self.assertIsNone(prop.parent)
        self.assertEqual(len(prop_parent.props), 0)

        with self.assertRaises(ValueError):
            Property("property_prop", parent=Property("P"))
        with self.assertRaises(ValueError):
            Property("property_doc", parent=Document())

    def test_dtype(self):
        prop = Property(name="prop")

        # Test assignment of all supported dtypes.
        for curr_type in DType:
            prop.dtype = curr_type
            self.assertEqual(prop.dtype, curr_type)

        # Test assignment of dtype alias.
        prop.dtype = "bool"
        self.assertEqual(prop.dtype, "bool")
        prop.dtype = "str"
        self.assertEqual(prop.dtype, "str")

        # Test assignment of tuple.
        prop.dtype = "2-tuple"
        self.assertEqual(prop.dtype, "2-tuple")

        # Test set None
        prop.dtype = None
        self.assertIsNone(prop.dtype)

        # Test assignment fails.
        with self.assertRaises(AttributeError):
            prop.dtype = 1
        with self.assertRaises(AttributeError):
            prop.dtype = "crash and burn"
        with self.assertRaises(AttributeError):
            prop.dtype = "x-tuple"

        # Test not setting None when a property contains values.
        prop.values = [1, 2, 3]
        self.assertIsNotNone(prop.dtype)
        prop.dtype = None
        self.assertIsNotNone(prop.dtype)

    def test_get_path(self):
        doc = Document()
        sec = Section(name="parent", parent=doc)

        # Check root path for a detached Property.
        prop = Property(name="prop")
        self.assertEqual("/", prop.get_path())

        # Check absolute path of Property in a Document.
        prop.parent = sec
        self.assertEqual("/%s:%s" % (sec.name, prop.name), prop.get_path())

    def test_id(self):
        prop = Property(name="P")
        self.assertIsNotNone(prop.id)

        prop = Property("P", oid="79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertEqual(prop.id, "79b613eb-a256-46bf-84f6-207df465b8f7")

        prop = Property("P", oid="id")
        self.assertNotEqual(prop.id, "id")

        # Make sure id cannot be reset programmatically.
        with self.assertRaises(AttributeError):
            prop.id = "someId"

    def test_new_id(self):
        prop = Property(name="prop")
        old_id = prop.id

        # Test assign new generated id.
        prop.new_id()
        self.assertNotEqual(old_id, prop.id)

        # Test assign new custom id.
        old_id = prop.id
        prop.new_id("79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertNotEqual(old_id, prop.id)
        self.assertEqual("79b613eb-a256-46bf-84f6-207df465b8f7", prop.id)

        # Test invalid custom id exception.
        with self.assertRaises(ValueError):
            prop.new_id("crash and burn")

    def test_merge_check(self):
        # Test dtype check
        source = Property(name="source", dtype="string")
        destination = Property(name="destination", dtype="string")

        destination.merge_check(source)
        source.dtype = "int"
        with self.assertRaises(ValueError):
            destination.merge_check(source)

        destination.merge_check(source, False)

        # Test value check
        source = Property(name="source", value=[1, 2, 3])
        destination = Property(name="destination", value=[4, 5, 6])
        destination.merge_check(source)

        # Test value convertable
        source = Property(name="source", value=["7", "8"])
        with self.assertRaises(ValueError):
            destination.merge_check(source)

        destination.merge_check(source, False)

        # Test value not convertable
        source = Property(name="source", value=["nine", "ten"])
        with self.assertRaises(ValueError):
            destination.merge_check(source)
        with self.assertRaises(ValueError):
            destination.merge_check(source, False)

        # Test unit check
        source = Property(name="source", unit="Hz")
        destination = Property(name="destination", unit="Hz")

        destination.merge_check(source)
        source.unit = "s"
        with self.assertRaises(ValueError):
            destination.merge_check(source)

        destination.merge_check(source, False)

        # Test uncertainty check
        source = Property(name="source", uncertainty=0.0)
        destination = Property(name="destination", uncertainty=0.0)

        destination.merge_check(source)
        source.uncertainty = 10.0
        with self.assertRaises(ValueError):
            destination.merge_check(source)

        destination.merge_check(source, False)

        # Test definition check
        source = Property(name="source", definition="Freude\t schoener\nGoetterfunken\n")
        destination = Property(name="destination",
                               definition="FREUDE schoener GOETTERfunken")

        destination.merge_check(source)
        source.definition = "Freunde schoender Goetterfunken"
        with self.assertRaises(ValueError):
            destination.merge_check(source)

        destination.merge_check(source, False)

        # Test reference check
        source = Property(name="source", reference="portal.g-node.org")
        destination = Property(name="destination", reference="portal.g-node.org")

        destination.merge_check(source)
        source.reference = "portal.g-node.org/odml/terminologies/v1.1"
        with self.assertRaises(ValueError):
            destination.merge_check(source)

        destination.merge_check(source, False)

        # Test value origin check
        source = Property(name="source", value_origin="file")
        destination = Property(name="destination", value_origin="file")

        destination.merge_check(source)
        source.value_origin = "other file"
        with self.assertRaises(ValueError):
            destination.merge_check(source)

        destination.merge_check(source, False)

    def test_merge(self):
        p_dst = Property("p1", value=[1, 2, 3], unit="Hz",
                         definition="Freude\t schoener\nGoetterfunken\n",
                         reference="portal.g-node.org", uncertainty=0.0, value_origin="file")
        p_src = Property("p2", value=[2, 4, 6], unit="Hz",
                         definition="FREUDE schoener GOETTERfunken")

        test_p = p_dst.clone()
        test_p.merge(p_src)
        self.assertEqual(len(test_p.values), 5)

        p_inv_unit = p_src.clone()
        p_inv_unit.unit = 's'

        p_inv_def = p_src.clone()
        p_inv_def.definition = "Freunde schoender Goetterfunken"

        p_inv_uncert = p_src.clone()
        p_inv_uncert.uncertainty = 10.0

        p_inv_ref = p_src.clone()
        p_inv_ref.reference = "test"

        p_inv_origin = p_src.clone()
        p_inv_origin.value_origin = "other file"

        test_p = p_dst.clone()
        self.assertRaises(ValueError, test_p.merge, p_inv_unit)
        self.assertRaises(ValueError, test_p.merge, p_inv_def)
        self.assertRaises(ValueError, test_p.merge, p_inv_uncert)
        self.assertRaises(ValueError, test_p.merge, p_inv_ref)
        self.assertRaises(ValueError, test_p.merge, p_inv_origin)

        test_p.reference = None
        test_p.merge(p_src)
        self.assertEqual(test_p.reference, p_src.reference)

        test_p.unit = ""
        test_p.merge(p_src)
        self.assertEqual(test_p.unit, p_src.unit)

        test_p.uncertainty = None
        test_p.merge(p_src)
        self.assertEqual(test_p.uncertainty, p_src.uncertainty)

        test_p.definition = ""
        test_p.merge(p_src)
        self.assertEqual(test_p.definition, p_src.definition)

        test_p.value_origin = ""
        test_p.merge(p_src)
        self.assertEqual(test_p.value_origin, p_src.value_origin)

        double_p = Property("adouble", value=3.14)
        int_p = Property("aint", value=3)
        self.assertRaises(ValueError, double_p.merge, int_p)

        int_p.merge(double_p, strict=False)
        self.assertEqual(len(int_p), 2)

    def test_clone(self):
        sec = Section(name="parent")

        # Check different id.
        prop = Property(name="original")
        clone_prop = prop.clone()
        self.assertNotEqual(prop.id, clone_prop.id)

        # Check parent removal in clone.
        prop.parent = sec
        clone_prop = prop.clone()
        self.assertIsNotNone(prop.parent)
        self.assertIsNone(clone_prop.parent)

        # Check keep_id
        prop = Property(name="keepid")
        clone_prop = prop.clone(True)
        self.assertEqual(prop.id, clone_prop.id)

    def test_get_merged_equivalent(self):
        sec = Section(name="parent")
        mersec = Section(name="merged_section")
        merprop_other = Property(name="other_prop", value="other")
        merprop = Property(name="prop", value=[1, 2, 3])

        # Check None on unset parent.
        prop = Property(name="prop")
        self.assertIsNone(prop.get_merged_equivalent())

        # Check None on parent without merged Section.
        prop.parent = sec
        self.assertIsNone(prop.get_merged_equivalent())

        # Check None on parent with merged Section but no attached Property.
        sec.merge(mersec)
        self.assertIsNone(prop.get_merged_equivalent())

        # Check None on parent with merged Section and unequal Property.
        merprop_other.parent = mersec
        self.assertIsNone(prop.get_merged_equivalent())

        # Check receiving merged equivalent Property.
        merprop.parent = mersec
        self.assertIsNotNone(prop.get_merged_equivalent())
        self.assertEqual(prop.get_merged_equivalent(), merprop)

    def test_comparison(self):
        p_name = "propertyName"
        p_origin = "from over there"
        p_unit = "pears"
        p_uncertainty = "+-12"
        p_ref = "4 8 15 16 23"
        p_def = "an odml test property"
        p_dep = "yes"
        p_dep_val = "42"
        p_val = ["a", "b"]

        prop_a = Property(name=p_name, value_origin=p_origin, unit=p_unit,
                          uncertainty=p_uncertainty, reference=p_ref, definition=p_def,
                          dependency=p_dep, dependency_value=p_dep_val, value=p_val)

        prop_b = Property(name=p_name, value_origin=p_origin, unit=p_unit,
                          uncertainty=p_uncertainty, reference=p_ref, definition=p_def,
                          dependency=p_dep, dependency_value=p_dep_val, value=p_val)

        self.assertEqual(prop_a, prop_b)

        prop_b.name = 'newPropertyName'
        self.assertNotEqual(prop_a, prop_b)

    def test_export_leaf(self):
        doc = Document()

        sec_a_name = "first"
        sec_b_name = "second"
        first = doc.create_section(sec_a_name)
        second = first.create_section(sec_b_name)
        _ = first.create_section("third")

        prop_aa = first.create_property("prop1", value=[1.3])
        _ = first.create_property("prop5", value=["abc"])
        prop_ba = second.create_property("prop2", value=["words"])
        _ = second.create_property("prop3", value=["a", "b"])
        _ = second.create_property("prop4", value=[3])

        export_doc = prop_aa.export_leaf()
        self.assertEqual(len(export_doc[sec_a_name].properties), 2)
        self.assertEqual(len(export_doc[sec_a_name].sections), 0)

        export_doc = prop_ba.export_leaf()
        self.assertEqual(len(export_doc.sections), 1)
        self.assertEqual(len(export_doc[sec_a_name].properties), 2)
        self.assertEqual(len(export_doc[sec_a_name].sections), 1)
        self.assertEqual(len(export_doc[sec_a_name][sec_b_name].properties), 3)

    def test_values_cardinality(self):
        doc = Document()
        sec = Section(name="sec", type="type", parent=doc)

        # -- Test set cardinality on Property init
        # Test empty init
        prop_card_none = Property(name="prop_cardinality_empty", parent=sec)
        self.assertIsNone(prop_card_none.val_cardinality)

        # Test single int max init
        prop_card_max = Property(name="prop_cardinality_max", val_cardinality=10, parent=sec)
        self.assertEqual(prop_card_max.val_cardinality, (None, 10))

        # Test tuple init
        prop_card_min = Property(name="prop_cardinality_min", val_cardinality=(2, None), parent=sec)
        self.assertEqual(prop_card_min.val_cardinality, (2, None))

        # -- Test Property cardinality re-assignment
        prop = Property(name="prop", val_cardinality=(None, 10), parent=sec)
        self.assertEqual(prop.val_cardinality, (None, 10))

        # Test Property cardinality reset
        for non_val in [None, "", [], ()]:
            prop.val_cardinality = non_val
            self.assertIsNone(prop.val_cardinality)
            prop.val_cardinality = 1

        # Test Property cardinality single int max assignment
        prop.val_cardinality = 10
        self.assertEqual(prop.val_cardinality, (None, 10))

        # Test Property cardinality tuple max assignment
        prop.val_cardinality = (None, 5)
        self.assertEqual(prop.val_cardinality, (None, 5))

        # Test Property cardinality tuple min assignment
        prop.val_cardinality = (5, None)
        self.assertEqual(prop.val_cardinality, (5, None))

        # Test Property cardinality min/max assignment
        prop.val_cardinality = (1, 5)
        self.assertEqual(prop.val_cardinality, (1, 5))

        # -- Test Property cardinality assignment failures
        with self.assertRaises(ValueError):
            prop.val_cardinality = "a"

        with self.assertRaises(ValueError):
            prop.val_cardinality = -1

        with self.assertRaises(ValueError):
            prop.val_cardinality = (1, "b")

        with self.assertRaises(ValueError):
            prop.val_cardinality = (1, 2, 3)

        with self.assertRaises(ValueError):
            prop.val_cardinality = (-1, 1)

        with self.assertRaises(ValueError):
            prop.val_cardinality = (1, -5)

        with self.assertRaises(ValueError):
            prop.val_cardinality = (5, 1)

    def test_set_values_cardinality(self):
        doc = Document()
        sec = Section(name="sec", type="sec_type", parent=doc)

        prop = Property(name="prop", val_cardinality=1, parent=sec)

        # Test Property values cardinality min assignment
        prop.set_values_cardinality(1)
        self.assertEqual(prop.val_cardinality, (1, None))

        # Test Property values cardinality keyword min assignment
        prop.set_values_cardinality(min_val=2)
        self.assertEqual(prop.val_cardinality, (2, None))

        # Test Property values cardinality max assignment
        prop.set_values_cardinality(None, 1)
        self.assertEqual(prop.val_cardinality, (None, 1))

        # Test Property values cardinality keyword max assignment
        prop.set_values_cardinality(max_val=2)
        self.assertEqual(prop.val_cardinality, (None, 2))

        # Test Property values cardinality min max assignment
        prop.set_values_cardinality(1, 2)
        self.assertEqual(prop.val_cardinality, (1, 2))

        # Test Property values cardinality keyword min max assignment
        prop.set_values_cardinality(min_val=2, max_val=5)
        self.assertEqual(prop.val_cardinality, (2, 5))

        # Test Property values cardinality empty reset
        prop.set_values_cardinality()
        self.assertIsNone(prop.val_cardinality)

        # Test Property values cardinality keyword empty reset
        prop.set_values_cardinality(1)
        self.assertIsNotNone(prop.val_cardinality)
        prop.set_values_cardinality(min_val=None, max_val=None)
        self.assertIsNone(prop.val_cardinality)
