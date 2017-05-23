import unittest
from odml import Section


class TestFindSections(unittest.TestCase):

    def setUp(self):
        self.root_section = Section("Type test", "test")
        self.root_section.append(Section("sub_1", "sub_1"))
        self.root_section.append(Section("sub_2", "sub_2"))
        self.root_section.append(Section("sub_2_b", "sub_2"))
        self.root_section.append(Section("sub_3", "sub_2/sub_3"))

    def test_find_by_name(self):
        ret = self.root_section.find("sub_1")
        self.assertTrue(ret.name == "sub_1")

        ret = self.root_section.find("unknown_type")
        self.assertIsNone(ret)

    def test_find_by_type(self):
        ret = self.root_section.find(type="sub_1")
        self.assertTrue(ret is not None and ret.type == "sub_1")

        ret = self.root_section.find(type="sub_2", findAll=True)
        self.assertTrue(len(ret) == 2)

        ret = self.root_section.find(key=None, type="sub_2", findAll=True,
                                     include_subtype=True)

        self.assertTrue(len(ret) == 3)

    def test_find_by_name_and_type(self):
        ret = self.root_section.find(key="sub_1", type="sub_1")
        self.assertTrue(ret.name == "sub_1")

        ret = self.root_section.find(key="sub_1", type="sub_2")
        self.assertIsNone(ret)
