import odml.gui.treemodel.mixin #this also provides event functionality, and we also test tree-based event passing
import odml.tools.event
import unittest
import samplefile
import odml

class TestEvents(unittest.TestCase):
    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        impl = odml.getImplementation()
        for obj in [impl.Value, impl.Property, impl.Section, impl.Document]:
            obj._Changed += self.event_success

    def tearDown(self):
        impl = odml.getImplementation()
        for obj in [impl.Value, impl.Property, impl.Section, impl.Document]:
            obj._Changed -= self.event_success

    def event_success(self, context):
        if context.preChange: return
        context.cur._modified = context._obj[:]
        context.cur._context  = context

    def test_simple_events(self):
        a = odml.Value(1)
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
        odml.getImplementation().Value._Changed += func
        a = odml.Value(1)
        a.value = 2
        odml.getImplementation().Value._Changed -= func
        self.assertEqual(res, [(True, False), (False, True)])

    def test_event_passing(self):
        s = odml.Section(name="section")
        v = odml.Value(1)
        p = odml.Property(name="prop", value=v)
        s.append(p)

        v.data = 4
        self.assertEqual(v._modified, [v])
        self.assertEqual(p._modified, [v, p])
        self.assertEqual(s._modified, [v, p, s])
        self.assertEqual(v.data, 4)
        #TODO integrate Document

    def test_change_context_getStack(self):
        c = odml.tools.event.ChangeContext(1)
        c._obj = [1]
        self.assertEqual(c.getStack(2), [None, 1])
        c._obj = [1, 2]
        self.assertEqual(c.getStack(2), [1, 2])
        c._obj = [1, 2, 3]
        self.assertEqual(c.getStack(2), [1, 2])

if __name__ == '__main__':
    unittest.main()

