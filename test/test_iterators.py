import unittest
from datetime import datetime as dt
from odml import Property, Section, Document

longago = dt.strptime('2013-08-11 09:48:49', "%Y-%m-%d %H:%M:%S")
recently = dt.strptime('2014-02-25 14:42:13', "%Y-%m-%d %H:%M:%S")


class TestValidation(unittest.TestCase):

    def setUp(self):
        """
        doc -- <section foo> -- <section subfoo>
                        \
                         -- <section bar> -- <section subbar>

        """
        doc = Document("author")

        foo = Section("foo", "footype")
        doc.append(foo)
        foo.append(Property("strprop", "somestring"))
        foo.append(Property("txtprop", "some\ntext"))

        subfoo = Section("subfoo", "footype")
        foo.append(subfoo)
        subfoo.append(Property("strprop", "somestring"))
        subfoo.append(Property("txtprop", "some\ntext"))

        bar = Section("bar", "bartype")
        foo.append(bar)
        bar.append(Property("strprop", "otherstring"))
        bar.append(Property("txtprop", "other\ntext"))

        subbar = Section("subbar", "bartype")
        bar.append(subbar)
        subbar.append(Property("strprop", "otherstring"))
        subbar.append(Property("txtprop", "other\ntext"))

        self.doc = doc

    def test_itersections(self):
        sec_all = self.doc.itersections()
        assert(len([s for s in sec_all]) == 4)

        filter_func = lambda x: getattr(x, 'name') == "foo"
        sec_filt = self.doc.itersections(filter_func=filter_func)
        assert(len([s for s in sec_filt]) == 1)

        filter_func = lambda x: getattr(x, 'type').find("bar") > -1
        sec_filt = self.doc.itersections(filter_func=filter_func)
        assert(len([s for s in sec_filt]) == 2)

        sec_filt = self.doc.itersections(max_depth=2)
        assert(len([s for s in sec_filt]) == 3)

        sec_filt = self.doc.itersections(max_depth=1)
        assert(len([s for s in sec_filt]) == 1)

        sec_filt = self.doc.itersections(max_depth=0)
        assert(len([s for s in sec_filt]) == 0)

    def test_iterproperties(self):
        prop_all = self.doc.iterproperties()
        assert(len([p for p in prop_all]) == 8)

        filter_func = lambda x: getattr(x, 'name').find("strprop") > -1
        prop_filt = self.doc.iterproperties(filter_func=filter_func)
        assert(len([p for p in prop_filt]) == 4)

        prop_filt = self.doc.iterproperties(
            filter_func=filter_func, max_depth=2)
        assert(len([p for p in prop_filt]) == 3)

        prop_filt = self.doc.iterproperties(filter_func=filter_func,
                                            max_depth=1)

        assert(len([p for p in prop_filt]) == 1)

    def test_itervalues(self):
        val_all = self.doc.itervalues()
        assert(len([v for v in val_all]) == 8)

        filter_func = lambda x: str(x).find("text") > -1
        val_filt = self.doc.itervalues(filter_func=filter_func)
        assert(len([v for v in val_filt]) == 4)

        val_filt = self.doc.itervalues(filter_func=filter_func, max_depth=2)
        assert(len([v for v in val_filt]) == 3)

        val_filt = self.doc.itervalues(filter_func=filter_func, max_depth=1)
        assert(len([v for v in val_filt]) == 1)
