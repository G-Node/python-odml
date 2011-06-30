import unittest

import odml.tools.treemodel.mixin
import odml.tools.gui.commands as commands
import samplefile

class TestCommands(unittest.TestCase):
    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        #for s in self.doc: xmlparser.dumpSection(s)

    def move_object(self, obj, src, dst):
        pos = obj.position
        self.assertIn(obj, src)
        #print obj.parent, pos
        #self.assertIs(obj, obj.parent[pos])

        cmd = commands.MoveObject(obj=obj, dst=dst)
        cmd()
        self.assertNotIn(obj, src)
        self.assertIn(obj, dst)
        self.assertIs(obj.parent, dst)

        cmd.undo()
        self.assertNotIn(obj, dst)
        self.assertIn(obj, src)
        self.assertIs(obj.parent, src)
        self.assertEqual(obj.position, pos)

    def test_section_move(self):
        self.move_object(
            obj=self.doc.sections[0].sections[1],
            src=self.doc.sections[0],
            dst=self.doc.sections[1])

    def test_property_move(self):
        print self.doc.sections[0]
        print self.doc.sections[0].sections[1]
        print self.doc.sections[0].sections[1].properties[1]

        self.move_object(
            obj=self.doc.sections[0].sections[1].properties[1],
            src=self.doc.sections[0].sections[1],
            dst=self.doc.sections[1])

    def test_value_move(self):
        """not yet needed"""
        pass

if __name__ == '__main__':
    unittest.main()

