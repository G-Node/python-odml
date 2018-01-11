import odml
import unittest

from odml.terminology import REPOSITORY


class BugTests(unittest.TestCase):

    def test_doc_repository_attribute_init(self):
        doc = odml.Document(repository=REPOSITORY)
        self.assertEqual(doc._repository, REPOSITORY,
                         "Document needs to init its baseclass first, "
                         "as it overwrites the repository attribute")
        self.assertEqual(doc.repository, REPOSITORY)
