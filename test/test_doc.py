import unittest

from odml import Document


class TestSection(unittest.TestCase):
    def setUp(self):
        pass

    def test_id(self):
        doc = Document()
        self.assertIsNotNone(doc.id)

        doc = Document("D", id="79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertEqual(doc.id, "79b613eb-a256-46bf-84f6-207df465b8f7")

        doc = Document("D", id="id")
        self.assertNotEqual(doc.id, "id")

        # Make sure id cannot be reset programmatically.
        with self.assertRaises(AttributeError):
            doc.id = "someId"

    def test_new_id(self):
        doc = Document()
        old_id = doc.id

        # Test assign new generated id.
        doc.new_id()
        self.assertNotEqual(old_id, doc.id)

        # Test assign new custom id.
        old_id = doc.id
        doc.new_id("79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertNotEqual(old_id, doc.id)
        self.assertEqual("79b613eb-a256-46bf-84f6-207df465b8f7", doc.id)

        # Test invalid custom id exception.
        with self.assertRaises(ValueError):
            doc.new_id("crash and burn")
