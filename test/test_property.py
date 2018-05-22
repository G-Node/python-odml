import unittest

from odml import Property, Section, Document, DType
from odml.property import BaseProperty
from odml.section import BaseSection


class TestProperty(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_attributes(self):
        p_name = "propertyName"
        p_origin = "from over there"
        p_unit = "pears"
        p_uncertainty = "+-12"
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
        prop.uncertainty = "%s_edit" % p_uncertainty
        self.assertEqual(prop.uncertainty, "%s_edit" % p_uncertainty)
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
        p = Property("property", 100)
        self.assertEqual(p.value[0], 100)
        self.assertIsInstance(p.value, list)

        p.value = None
        self.assertEqual(len(p), 0)

        p.value = [1, 2, 3]
        p.value = ""
        self.assertEqual(len(p), 0)

        p.value = [1, 2, 3]
        p.value = []
        self.assertEqual(len(p), 0)

        p.value = [1, 2, 3]
        p.value = ()
        self.assertEqual(len(p), 0)

        p.value.append(5)
        self.assertEqual(len(p.value), 0)

        p2 = Property("test", {"name": "Marie", "name": "Johanna"})
        self.assertEqual(len(p2), 1)

        # Test tuple dtype value.
        t = Property(name="Location", value='(39.12; 67.19)', dtype='2-tuple')
        tuple_value = t.value[0]  # As the formed tuple is a list of list
        self.assertEqual(tuple_value[0], '39.12')
        self.assertEqual(tuple_value[1], '67.19')

        # Test invalid tuple length
        with self.assertRaises(ValueError):
            _ = Property(name="Public-Key", value='(5689; 1254; 687)', dtype='2-tuple')

    def test_value_append(self):
        # Test append w/o Property value or dtype
        prop = Property(name="append")
        prop.append(1)
        self.assertEqual(prop.dtype, DType.int)
        self.assertEqual(prop.value, [1])

        # Test append with Property dtype.
        prop = Property(name="append", dtype="int")
        prop.append(3)
        self.assertEqual(prop.value, [3])

        # Test append with Property value
        prop = Property(name="append", value=[1, 2])
        prop.append(3)
        self.assertEqual(prop.value, [1, 2, 3])

        # Test append with Property list value
        prop = Property(name="append", value=[1, 2])
        prop.append([3])
        self.assertEqual(prop.value, [1, 2, 3])

        # Test append of empty values, make sure 0 and False are properly handled
        prop = Property(name="append")
        prop.append(None)
        prop.append("")
        prop.append([])
        prop.append({})
        self.assertEqual(prop.value, [])

        prop.append(0)
        self.assertEqual(prop.value, [0])

        prop.value = None
        prop.dtype = None
        prop.append(False)
        self.assertEqual(prop.value, [False])

        prop = Property(name="append", value=[1, 2])
        prop.append(None)
        prop.append("")
        prop.append([])
        prop.append({})
        self.assertEqual(prop.value, [1, 2])

        prop.append(0)
        self.assertEqual(prop.value, [1, 2, 0])

        # Test fail append with multiple values
        prop = Property(name="append", value=[1, 2, 3])
        with self.assertRaises(ValueError):
            prop.append([4, 5])
        self.assertEqual(prop.value, [1, 2, 3])

        # Test fail append with mismatching dtype
        prop = Property(name="append", value=[1, 2], dtype="int")
        with self.assertRaises(ValueError):
            prop.append([3.14])
        with self.assertRaises(ValueError):
            prop.append([True])
        with self.assertRaises(ValueError):
            prop.append(["5.927"])
        self.assertEqual(prop.value, [1, 2])

        # Test strict flag
        prop.append(3.14, strict=False)
        prop.append(True, strict=False)
        prop.append("5.927", strict=False)
        self.assertEqual(prop.value, [1, 2, 3, 1, 5])

        # Make sure non-convertible values still raise an error
        with self.assertRaises(ValueError):
            prop.append("invalid")
        self.assertEqual(prop.value, [1, 2, 3, 1, 5])

        p5 = Property("test", value="a string")
        p5.append("Freude")
        self.assertEqual(len(p5), 2)
        self.assertRaises(ValueError, p5.append, "[a, b, c]")

    def test_value_extend(self):
        prop = Property(name="extend")

        # Test extend w/o Property value or dtype.
        val = [1, 2, 3]
        prop.extend(val)
        self.assertEqual(prop.dtype, DType.int)
        self.assertEqual(prop.value, val)

        # Extend with single value.
        prop.extend(4)
        self.assertEqual(prop.value, [1, 2, 3, 4])

        # Extend with list value.
        prop.extend([5, 6])
        self.assertEqual(prop.value, [1, 2, 3, 4, 5, 6])

        # Test extend w/o Property value
        prop = Property(name="extend", dtype="float")
        prop.extend([1.0, 2.0, 3.0])
        self.assertEqual(prop.value, [1.0, 2.0, 3.0])

        # Test extend with Property value
        prop = Property(name="extend", value=10)
        prop.extend([20, 30, '40'])
        self.assertEqual(prop.value, [10, 20, 30, 40])

        # Test extend fail with mismatching dtype
        with self.assertRaises(ValueError):
            prop.extend(['5', 6, 7])
        with self.assertRaises(ValueError):
            prop.extend([5, 6, 'a'])

        # Test extend via Property
        prop = Property(name="extend", value=["a", "b"])
        ext_prop = Property(name="value extend", value="c")
        prop.extend(ext_prop)
        self.assertEqual(prop.value, ["a", "b", "c"])

        ext_prop.value = ["d", "e"]
        prop.extend(ext_prop)
        self.assertEqual(prop.value, ["a", "b", "c", "d", "e"])

        ext_prop = Property(name="value extend", value=[1, 2 ,3])
        with self.assertRaises(ValueError):
            prop.extend(ext_prop)
        self.assertEqual(prop.value, ["a", "b", "c", "d", "e"])

        # Test extend via Property unit check
        prop = Property(name="extend", value=[1, 2], unit="mV")
        ext_prop = Property(name="extend", value=[3, 4], unit="mV")
        prop.extend(ext_prop)
        self.assertEqual(prop.value, [1, 2, 3, 4])

        ext_prop.unit = "kV"
        with self.assertRaises(ValueError):
            prop.extend(ext_prop)
        self.assertEqual(prop.value, [1, 2, 3, 4])

        ext_prop.unit = ""
        with self.assertRaises(ValueError):
            prop.extend(ext_prop)
        self.assertEqual(prop.value, [1, 2, 3, 4])

        # Test strict flag
        prop = Property(name="extend", value=[1, 2], dtype="int")
        with self.assertRaises(ValueError):
            prop.extend([3.14, True, "5.927"])
        self.assertEqual(prop.value, [1, 2])

        prop.extend([3.14, True, "5.927"], strict=False)
        self.assertEqual(prop.value, [1, 2, 3, 1, 5])

        # Make sure non-convertible values still raise an error
        with self.assertRaises(ValueError):
            prop.extend([6, "some text"])

    def test_get_set_value(self):
        values = [1, 2, 3, 4, 5]
        p = Property("property", value=values)

        self.assertEqual(len(p), 5)
        for s, d in zip(values, p.value):
            self.assertEqual(s, d)

        count = 0
        for v in p:
            count += 1
        self.assertEqual(count, len(values))

        p[0] = 10
        self.assertEqual(p[0], 10)
        with self.assertRaises(ValueError):
            p[1] = 'stringval'

    def test_bool_conversion(self):
        # Success tests
        p = Property(name='received', value=[1, 0, 1, 0, 1])
        assert(p.dtype == 'int')
        p.dtype = DType.boolean
        assert(p.dtype == 'boolean')
        assert(p.value == [True, False, True, False, True])

        q = Property(name='sent', value=['False', True, 'TRUE', '0', 't', 'F', '1'])
        assert(q.dtype == 'string')
        q.dtype = DType.boolean
        assert(q.dtype == 'boolean')
        assert(q.value == [False, True, True, False, True, False, True])

        # Failure tests
        curr_val = [3, 0, 1, 0, 8]
        curr_type = 'int'
        p = Property(name='received', value=curr_val)
        assert(p.dtype == curr_type)
        with self.assertRaises(ValueError):
            p.dtype = DType.boolean
        assert(p.dtype == curr_type)
        assert(p.value == curr_val)

        curr_type = 'string'
        q = Property(name='sent', value=['False', True, 'TRUE', '0', 't', '12', 'Ft'])
        assert(q.dtype == curr_type)
        with self.assertRaises(ValueError):
            q.dtype = DType.boolean
        assert(q.dtype == curr_type)

    def test_str_to_int_convert(self):
        # Success Test
        p = Property(name='cats_onboard', value=['3', '0', '1', '0', '8'])
        assert(p.dtype == 'string')
        p.dtype = DType.int
        assert(p.dtype == 'int')
        assert(p.value == [3, 0, 1, 0, 8])

        # Failure Test
        p = Property(name='dogs_onboard', value=['7', '20', '1 Dog', 'Seven'])
        assert(p.dtype == 'string')

        with self.assertRaises(ValueError):
            p.dtype = DType.int

        assert(p.dtype == 'string')
        assert(p.value == ['7', '20', '1 Dog', 'Seven'])

    def test_name(self):
        # Test id is used when name is not provided
        p = Property()
        self.assertIsNotNone(p.name)
        self.assertEqual(p.name, p.id)

        # Test name is properly set on init
        name = "rumpelstilzchen"
        p = Property(name)
        self.assertEqual(p.name, name)

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
        p = Property("property_section", parent=Section("S"))
        self.assertIsInstance(p.parent, BaseSection)
        self.assertEqual(len(p.parent._props), 1)

        """ Test if child is removed from _props of a parent after assigning
            a new parent to the child """
        prop_parent = p.parent
        p.parent = Section("S1")
        self.assertEqual(len(prop_parent._props), 0)
        self.assertIsInstance(p.parent, BaseSection)
        self.assertIsInstance(p.parent._props[0], BaseProperty)

        prop_parent = p.parent
        p.parent = None
        self.assertIsNone(p.parent)
        self.assertEqual(len(prop_parent._props), 0)

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
        prop.value = [1, 2, 3]
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
        p = Property(name="P")
        self.assertIsNotNone(p.id)

        p = Property("P", oid="79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertEqual(p.id, "79b613eb-a256-46bf-84f6-207df465b8f7")

        p = Property("P", oid="id")
        self.assertNotEqual(p.id, "id")

        # Make sure id cannot be reset programmatically.
        with self.assertRaises(AttributeError):
            p.id = "someId"

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
        p_dst = Property("p1", value=[1, 2, 3], unit="Hz", definition="Freude\t schoener\nGoetterfunken\n",
                         reference="portal.g-node.org", uncertainty=0.0, value_origin="file")
        p_src = Property("p2", value=[2, 4, 6], unit="Hz", definition="FREUDE schoener GOETTERfunken")

        test_p = p_dst.clone()
        test_p.merge(p_src)
        self.assertEqual(len(test_p.value), 5)

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


if __name__ == "__main__":
    print("TestProperty")
    tp = TestProperty()
    tp.test_value()
    tp.test_merge()
