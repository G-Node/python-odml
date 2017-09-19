import unittest
import odml

class TestTerminolgies(unittest.TestCase):
    def setUp(self):
        pass

    def test_load(self):
        if not odml.terminology.terminologies.empty():
            odml.terminology.terminologies.clear()
        self.assertTrue(odml.terminology.terminologies.empty())

    def test_cached_files(self):
        odml.terminology.clear_cache()
        self.assertTrue(len(odml.terminology.cached_files()) == 0)
        odml.terminology.load()
        self.assertTrue(len(odml.terminology.cached_files()) > 0)

    def test_from_cache(self):
        if not odml.terminology.terminologies.empty():
            odml.terminology.terminologies.clear()
        odml.terminology.from_cache(odml.terminology.terminologies)
        self.assertTrue(odml.terminology.terminologies.empty() == False)

    def test_find_difinitions(self):
        if odml.terminology.terminologies.empty():
            odml.terminology.from_cache(odml.terminology.terminologies)

        self.assertTrue(len(odml.terminology.find_definitions("analysis")) > 0)
        self.assertTrue(len(odml.terminology.find_definitions("foo")) == 0)

    def test_get_section(self):
        self.assertIsNone(odml.terminology.get_section_by_type("analyses"))
        self.assertIsNotNone(odml.terminology.get_section_by_type("analysis"))
        self.assertIsInstance(odml.terminology.get_section_by_type("analysis"), odml.section.BaseSection)
        self.assertIsNone(odml.terminology.get_section_by_type("analysis", "!g-node"))
        self.assertTrue(len((odml.terminology.get_section_by_type("setup/daq", "g-node"))) > 0)

