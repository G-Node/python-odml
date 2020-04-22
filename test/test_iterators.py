import unittest

from odml import Property, Section, Document


class TestValidation(unittest.TestCase):

    def setUp(self):
        """
        doc -- <section sec_main> -- <section sub_main>
                        \
                         -- <section sec_branch> -- <section sub_branch>
        """
        doc = Document("author")

        sec_main = Section("sec_main", "maintype")
        doc.append(sec_main)
        sec_main.append(Property("strprop", "somestring"))
        sec_main.append(Property("txtprop", "some\ntext"))

        sub_main = Section("sub_main", "maintype")
        sec_main.append(sub_main)
        sub_main.append(Property("strprop", "somestring"))
        sub_main.append(Property("txtprop", "some\ntext"))

        sec_branch = Section("sec_branch", "branchtype")
        sec_main.append(sec_branch)
        sec_branch.append(Property("strprop", "otherstring"))
        sec_branch.append(Property("txtprop", "other\ntext"))

        sub_branch = Section("sub_branch", "branchtype")
        sec_branch.append(sub_branch)
        sub_branch.append(Property("strprop", "otherstring"))
        sub_branch.append(Property("txtprop", "other\ntext"))

        self.doc = doc

    def test_itersections(self):
        sec_all = list(self.doc.itersections())
        self.assertEqual(len(sec_all), 4)

        filter_func = lambda x: getattr(x, "name") == "sec_main"
        sec_filtered = list(self.doc.itersections(filter_func=filter_func))
        self.assertEqual(len(sec_filtered), 1)

        filter_func = lambda x: getattr(x, "type").find("branch") > -1
        sec_filtered = list(self.doc.itersections(filter_func=filter_func))
        self.assertEqual(len(sec_filtered), 2)

        sec_filtered = list(self.doc.itersections(max_depth=2))
        self.assertEqual(len(sec_filtered), 3)

        sec_filtered = list(self.doc.itersections(max_depth=1))
        self.assertEqual(len(sec_filtered), 1)

        sec_filtered = list(self.doc.itersections(max_depth=0))
        self.assertEqual(len(sec_filtered), 0)

    def test_iterproperties(self):
        prop_all = list(self.doc.iterproperties())
        self.assertEqual(len(prop_all), 8)

        filter_func = lambda x: getattr(x, "name").find("strprop") > -1
        prop_filtered = list(self.doc.iterproperties(filter_func=filter_func))
        self.assertEqual(len(prop_filtered), 4)

        prop_filtered = list(self.doc.iterproperties(filter_func=filter_func, max_depth=2))
        self.assertEqual(len(prop_filtered), 3)

        prop_filtered = list(self.doc.iterproperties(filter_func=filter_func, max_depth=1))
        self.assertEqual(len(prop_filtered), 1)

    def test_itervalues(self):
        val_all = list(self.doc.itervalues())
        self.assertEqual(len(val_all), 8)

        filter_func = lambda x: str(x).find("text") > -1
        val_filtered = list(self.doc.itervalues(filter_func=filter_func))
        self.assertEqual(len(val_filtered), 4)

        val_filtered = list(self.doc.itervalues(filter_func=filter_func, max_depth=2))
        self.assertEqual(len(val_filtered), 3)

        val_filtered = list(self.doc.itervalues(filter_func=filter_func, max_depth=1))
        self.assertEqual(len(val_filtered), 1)
