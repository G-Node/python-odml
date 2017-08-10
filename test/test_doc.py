import unittest

from odml import Document


class TestSection(unittest.TestCase):
    def setUp(self):
        pass

    def test_set_id(self):
        d = Document("D", id="79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertEqual(d.id, "79b613eb-a256-46bf-84f6-207df465b8f7")

        Document("D", id="id")
        self.assertNotEqual(d.id, "id")
