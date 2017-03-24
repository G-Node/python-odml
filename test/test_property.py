import unittest
from odml import Property, Section, Document, DType


class TestProperty(unittest.TestCase):

    def setUp(self):
        pass

    def test_value(self):
        p = Property("property", 100)
        assert(p.value[0] == 100)

    def test_bool_conversion(self):

        p = Property(name='received', value=[3, 0, 1, 0, 8])
        assert(p.dtype == 'int')
        p.dtype = DType.boolean
        assert(p.dtype == 'boolean')
        assert(p.value == [True, False, True, False, True])

        q = Property(name='sent', value=['False', True, 'TRUE', '0'])
        assert(q.dtype == 'string')
        q.dtype = DType.boolean
        assert(q.dtype == 'boolean')
        assert(q.value == [False, True, True, False])

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
        try:
            p.dtype = DType.int
        except ValueError as e:
            assert(str(e) == "cannot convert from 'string' to 'int'")

        assert(p.dtype == 'string')
        assert(p.value == ['7', '20', '1 Dog', 'Seven'])

    def test_name(self):
        pass

    def test_parent(self):
        pass

    def test_dtype(self):
        pass

    def test_path(self):
        pass

if __name__ == "__main__":
    print("TestProperty")
    tp = TestProperty()
    tp.test_value()
