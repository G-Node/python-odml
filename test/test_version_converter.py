import io
import re
import unittest
from contextlib import contextmanager

from lxml import etree as ET

from odml.tools.version_converter import VersionConverter

try:
    unicode = unicode
except NameError:
    unicode = str

VS = VersionConverter


class TestVersionConverter(unittest.TestCase):
    def setUp(self):
        self.doc = """
                     <odML version="1">
                        <date>2008-07-07</date>
                        <section>
                            <property>
                                <value>0<unit>deg</unit><type>int</type><uncertainty/></value>
                                <value>45<unit>deg</unit><type>int</type></value>
                                <name>Orientations</name>
                            </property>
                            <type>some sec type</type>
                            <name>sec_name</name>
                        </section>
                        <section>
                            <type>some sec type</type>
                            <name>sec_name</name>
                            <property>
                                <name>prop_name</name>
                            </property>
                            <property>
                                <name>prop_name</name>
                            </property>
                        </section>
                        <author>Author</author>
                     </odML>
                   """

    @contextmanager
    def assertNotRaises(self, exc_type):
        try:
            yield None
        except exc_type:
            raise self.failureException('{} raised'.format(exc_type.__name__))

    def test_replace_same_name_entites(self):
        root = ET.fromstring(self.doc)
        sec_names = []
        sec_elems = []
        for sec in root.iter("section"):
            sec_names.append(sec.find("name").text)
            sec_elems.append(sec)
        self.assertEqual(sec_names[0], "sec_name")
        self.assertEqual(sec_names[0], sec_names[1])

        props_names = []
        for prop in sec_elems[1].iter("property"):
            props_names.append(prop.find("name").text)
        self.assertEqual(props_names[0], "prop_name")
        self.assertEqual(props_names[0], props_names[1])

        tree = ET.ElementTree(root)
        tree = VS._replace_same_name_entities(tree)
        root = tree.getroot()
        sec_names = []
        sec_elems = []
        for sec in root.iter("section"):
            sec_names.append(sec.find("name").text)
            sec_elems.append(sec)
        self.assertEqual(sec_names[0], "sec_name")
        self.assertEqual(sec_names[1], "sec_name-2")

        props_names = []
        for prop in sec_elems[1].iter("property"):
            props_names.append(prop.find("name").text)
        self.assertEqual(props_names[0], "prop_name")
        self.assertEqual(props_names[1], "prop_name-2")

    def test_fix_unmatching_tags(self):
        first_elem = list(VS._error_strings.keys())[0]
        self.doc = re.sub("<value>", "<value>" + first_elem, self.doc, count=1)
        file = io.StringIO(unicode(self.doc))
        with self.assertRaises(Exception):
            ET.fromstring(file.getvalue())
        file = VS._fix_unmatching_tags(file)
        with self.assertNotRaises(Exception):
            ET.fromstring(file.getvalue())

    def test_convert_odml_file(self):
        self.assertEqual(VS.convert_odml_file("/not_valid_path"), None)
        root = ET.fromstring(self.doc)
        prop = root.find("section").find("property")
        val_elems = []
        for val in prop.iter("value"):
            val_elems.append(val)

        self.assertEqual(val_elems[0].find("unit").text, "deg")
        self.assertEqual(val_elems[0].find("type").text, "int")
        self.assertEqual(val_elems[0].find("uncertainty").text, None)
        self.assertEqual(prop.find("unit"), None)
        self.assertEqual(prop.find("type"), None)

        file = io.StringIO(unicode(self.doc))
        tree = VS.convert_odml_file(file)
        root = tree.getroot()
        prop = root.find("section").find("property")
        val_elems = []
        for val in prop.iter("value"):
            val_elems.append(val)

        self.assertEqual(len(val_elems), 1)
        self.assertEqual(val_elems[0].find("unit"), None)
        self.assertEqual(val_elems[0].find("type"), None)
        self.assertEqual(val_elems[0].find("uncertainty"), None)
        self.assertEqual(val_elems[0].text, "0, 45")
        self.assertEqual(prop.find("unit").text, "deg")
        self.assertEqual(len(prop.findall("unit")), 1)
        self.assertEqual(prop.find("type").text, "int")
        self.assertEqual(len(prop.findall("type")), 1)
        self.assertEqual(prop.find("uncertainty").text, None)
