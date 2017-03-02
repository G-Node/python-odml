import unittest
from odml import Property, Section, Document


class TestProperty(unittest.TestCase):

    def setUp(self):
        pass

    def test_value(self):
        p = Property("property", 100)
        assert(p.value[0] == 100)

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
