import odml.tools.treemodel.mixin #this also provides event functionality, and we also test tree-based event passing
import unittest
import samplefile
from odml import doc, section, property, value

class TestEvents(unittest.TestCase):
    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        for obj in [value.Value, property.Property, section.Section, doc.Document]:
            obj._Changed += self.event_success

    def tearDown(self):
        for obj in [value.Value, property.Property, section.Section, doc.Document]:
            obj._Changed -= self.event_success

    def event_success(self, context):
        if context.preChange: return
        context.cur._modified = context._obj[:]
        context.cur._context  = context

    def test_simple_events(self):
        a = value.Value(1)
        a._value = 2
        self.assertEqual(a.data, 2)
        # modifying a protected attribute should not make a call,
        # thus the _modified property won't be set
        self.assertRaises(AttributeError, lambda: a._modified)

        a.data = 3
        self.assertEqual(a.data, 3)
        self.assertIs(a._modified[0], a)
        self.assertEqual(a._context.val, ("data", 3))
        self.assertTrue(a._context.postChange)

    def test_pre_post_change(self):
        res = []
        func = lambda context: res.append((context.preChange, context.postChange))
        value.Value._Changed += func
        a = value.Value(1)
        a.value = 2
        value.Value._Changed -= func
        self.assertEqual(res, [(True, False), (False, True)])

    def test_event_passing(self):
        s = section.Section(name="section")
        v = value.Value(1)
        p = property.Property(name="prop", value=v)
        s.append(p)

        v.data = 4
        self.assertEqual(v._modified, [v])
        self.assertEqual(p._modified, [v, p])
        self.assertEqual(s._modified, [v, p, s])
        self.assertEqual(v.data, 4)
        #TODO integrate Document

if __name__ == '__main__':
    unittest.main()

