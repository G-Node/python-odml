import odml
import unittest


class BugTests(unittest.TestCase):

    def test_doc_repository_attribute_init(self):
        repo = "http://portal.g-node.org/odml/terminologies/v1.0/" \
               "terminologies.xml"
        doc = odml.Document(repository=repo)
        self.assertEqual(doc._repository, repo,
                         "Document needs to init its baseclass first, "
                         "as it overwrites the repository attribute")
        self.assertEqual(doc.repository, repo)
