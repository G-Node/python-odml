import unittest

from odml import Property, Section, Document, DType
from odml.property import BaseProperty
from odml.section import BaseSection


class TestProperty(unittest.TestCase):

    def setUp(self):
        pass

    def test_value(self):
        p = Property("property", 100)
        self.assertEqual(p.value[0], 100)
        self.assertEqual(type(p.value), tuple)

        p.append(10)
        self.assertEqual(len(p.value), 2)
        p.append([20, 30, '40'])
        self.assertEqual(len(p.value), 5)
        with self.assertRaises(ValueError):
            p.append('invalid')
            p.append(('5', 6, 7))

        p2 = Property("property 2", 3)
        p.append(p2)
        self.assertEqual(len(p.value), 6)

        p.value = None
        self.assertEqual(len(p.value), 0)

        p.value = [1, 2, 3]
        p.value = ""
        self.assertEqual(len(p.value), 0)

        p.value = [1, 2, 3]
        p.value = []
        self.assertEqual(len(p.value), 0)

        p.value = [1, 2, 3]
        p.value = ()
        self.assertEqual(len(p.value), 0)

        p3 = Property("test", value=2, unit="Hz")
        p4 = Property("test", value=5.5, unit="s")

        with self.assertRaises(ValueError):
            p3.append(p4)

    def test_bool_conversion(self):

        # Success tests
        p = Property(name='received', value=[1, 0, 1, 0, 1])
        assert(p.dtype == 'int')
        p.dtype = DType.boolean
        assert(p.dtype == 'boolean')
        assert(p.value == (True, False, True, False, True))

        q = Property(name='sent', value=['False', True, 'TRUE', '0', 't', 'F', '1'])
        assert(q.dtype == 'string')
        q.dtype = DType.boolean
        assert(q.dtype == 'boolean')
        assert(q.value == (False, True, True, False, True, False, True))

        # Failure tests
        curr_val = [3, 0, 1, 0, 8]
        curr_type = 'int'
        p = Property(name='received', value=curr_val)
        assert(p.dtype == curr_type)
        with self.assertRaises(ValueError):
            p.dtype = DType.boolean
        assert(p.dtype == curr_type)
        assert(p.value == tuple(curr_val))

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
        assert(p.value == (3, 0, 1, 0, 8))

        # Failure Test
        p = Property(name='dogs_onboard', value=['7', '20', '1 Dog', 'Seven'])
        assert(p.dtype == 'string')

        with self.assertRaises(ValueError):
            p.dtype = DType.int

        assert(p.dtype == 'string')
        assert(p.value == ('7', '20', '1 Dog', 'Seven'))

    def test_name(self):
        pass

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
        pass

    def test_path(self):
        pass

    def test_value_origin(self):
        p = Property("P")
        self.assertEqual(p.value_origin, None)
        p = Property("P", value_origin="V")
        self.assertEqual(p.value_origin, "V")

    def test_set_id(self):
        p = Property("P", id="79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertEqual(p.id, "79b613eb-a256-46bf-84f6-207df465b8f7")

        Property("P", id="id")
        self.assertNotEqual(p.id, "id")

    def test_merge(self):
        p_dst = Property("p1", value=[1, 2, 3], unit="Hz", definition="Freude\t schoener\nGoetterfunken\n",
                         reference="portal.g-node.org", uncertainty=0.0)
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

        test_p = p_dst.clone()
        self.assertRaises(ValueError, test_p.merge, p_inv_unit)
        self.assertRaises(ValueError, test_p.merge, p_inv_def)
        self.assertRaises(ValueError, test_p.merge, p_inv_uncert)
        self.assertRaises(ValueError, test_p.merge, p_inv_ref)

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


if __name__ == "__main__":
    print("TestProperty")
    tp = TestProperty()
    tp.test_value()
    tp.test_merge()
