import odml.tools.treemodel.mixin #this also provides event functionality, and we also test tree-based event passing
import unittest
import samplefile
from odml import doc, section, property, value

class TestEvents(unittest.TestCase):
    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        for obj in [value.Value, property.Property, section.Section, doc.Document]:
            obj._Changed += self.event_success
    
    def event_success(self, obj, **kwargs):
        obj._modified = kwargs
        
    def test_simple_events(self):
        a = value.Value(1)
        a._value = 2
        self.assertEqual(a.data, 2)
        # modifying a protected attribute should not make a call,
        # thus the _modified property won't be set
        self.assertRaises(AttributeError, lambda: a._modified)
        
        a.data = 3
        self.assertEqual(a._modified, {})
        self.assertEqual(a.data, 3)

    def test_event_passing(self):
        s = section.Section(name="section")
        v = value.Value(1)
        p = property.Property(name="prop", value=v)
        s.append(p)
        
        v.data = 4
        self.assertEqual(v._modified, {})
        self.assertEqual(p._modified, {'value': v, 'value_pos': 0})
        self.assertEqual(s._modified, {'value': v, 'value_pos': 0, 'prop': p, 'prop_pos': 0})
        self.assertEqual(v.data, 4)
        #TODO integrate Document
        
if __name__ == '__main__':
    unittest.main()

