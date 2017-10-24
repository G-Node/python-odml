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

VC = VersionConverter


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
        tree = VC._replace_same_name_entities(tree)
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
        first_elem = list(VC._error_strings.keys())[0]
        self.doc = re.sub("<value>", "<value>" + first_elem, self.doc, count=1)
        file = io.StringIO(unicode(self.doc))
        with self.assertRaises(Exception):
            ET.fromstring(file.getvalue())
        file = VC._fix_unmatching_tags(file)
        with self.assertNotRaises(Exception):
            ET.fromstring(file.getvalue())

    def test_convert_odml_file(self):
        self.assertEqual(VC.convert_odml_file("/not_valid_path"), None)
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
        tree = VC.convert_odml_file(file)
        root = tree.getroot()
        prop = root.find("section").find("property")
        val_elems = []
        for val in prop.iter("value"):
            val_elems.append(val)

        self.assertEqual(len(val_elems), 1)
        self.assertEqual(val_elems[0].find("unit"), None)
        self.assertEqual(val_elems[0].find("type"), None)
        self.assertEqual(val_elems[0].find("uncertainty"), None)
        self.assertEqual(val_elems[0].text, "[0, 45]")
        self.assertEqual(prop.find("unit").text, "deg")
        self.assertEqual(len(prop.findall("unit")), 1)
        self.assertEqual(prop.find("type").text, "int")
        self.assertEqual(len(prop.findall("type")), 1)
        self.assertEqual(prop.find("uncertainty").text, None)

    def test_convert_odml_file_document(self):
        """Test proper conversion of the odml.Document entity from
        odml model version 1 to version 1.1.

        The test checks for the proper conversion of all valid
        Document tags and exclusion of non-Document tags.
        """

        doc = """
                <odML version="1">
                  <!-- Valid Document tags test -->
                  <author>Document author</author>
                  <version>1</version>
                  <date>2017-10-18</date>
                  <repository>Document repository</repository>
                  <section><name>Document section</name></section>
                
                  <!-- Unsupported Document tags test -->
                  <invalid>Invalid Document tag</invalid>
                  <property>Invalid Document property</property>
                  <value>Invalid Document value</value>
                </odML>
        """

        file = io.StringIO(unicode(doc))
        conv_doc = VC.convert_odml_file(file)
        root = conv_doc.getroot()
        # Test export of Document tags
        self.assertEqual(len(root.findall("author")), 1)
        self.assertEqual(len(root.findall("date")), 1)
        self.assertEqual(len(root.findall("repository")), 1)
        self.assertEqual(len(root.findall("section")), 1)

        # Test absence of non-Document tags
        self.assertEqual(len(root.findall("invalid")), 0)
        self.assertEqual(len(root.findall("property")), 0)
        self.assertEqual(len(root.findall("value")), 0)

    def test_convert_odml_file_section(self):
        """Test proper conversion of the odml.Section entity from
        odml model version 1 to version 1.1.

        The test checks for the proper conversion of all valid
        Section tags and exclusion of non-Section tags.
        """

        doc = """
                <odML version="1">
                  <!-- Valid Section tags test -->
                  <section>
                    <name>Section name</name>
                    <type>Section type</type>
                    <definition>Section definition</definition>
                    <reference>Section reference</reference>
                    <link>Section link</link>
                    <repository>Section repository</repository>
                    <include>Section include</include>
                    <property><name>Section Property 1</name></property>
                    <property><name>Section Property 2</name></property>
                
                    <section>
                      <name>SubSection name</name>
                      <type>SubSection type</type>
                      <definition>SubSection definition</definition>
                      <reference>SubSection reference</reference>
                      <link>SubSection link</link>
                      <repository>SubSection repository</repository>
                      <include>SubSection include</include>
                      <property><name>SubSection Property</name></property>
                    </section>
                  </section>
                
                  <section>
                    <name>Unsupported Section tags test</name>
                    <invalid>Invalid tag</invalid>
                    <value>Invalid Value tag</value>
                    <mapping>Unsupported mapping tag</mapping>
                  </section>
                </odML>
        """

        file = io.StringIO(unicode(doc))
        conv_doc = VC.convert_odml_file(file)
        root = conv_doc.getroot()

        sec = root.findall("section")
        self.assertEqual(len(sec), 2)

        # Test valid section tags
        self.assertEqual(len(sec[0]), 10)
        self.assertEqual(sec[0].find("name").text, "Section name")
        self.assertEqual(sec[0].find("type").text, "Section type")
        self.assertEqual(sec[0].find("definition").text, "Section definition")
        self.assertEqual(sec[0].find("reference").text, "Section reference")
        self.assertEqual(sec[0].find("link").text, "Section link")
        self.assertEqual(sec[0].find("repository").text, "Section repository")
        self.assertEqual(sec[0].find("include").text, "Section include")
        self.assertEqual(len(sec[0].findall("property")), 2)
        self.assertEqual(len(sec[0].findall("section")), 1)

        # Test valid subsection tags
        subsec = sec[0].find("section")
        self.assertEqual(len(subsec), 8)
        self.assertEqual(subsec.find("name").text, "SubSection name")
        self.assertEqual(subsec.find("type").text, "SubSection type")
        self.assertEqual(subsec.find("definition").text, "SubSection definition")
        self.assertEqual(subsec.find("reference").text, "SubSection reference")
        self.assertEqual(subsec.find("link").text, "SubSection link")
        self.assertEqual(subsec.find("repository").text, "SubSection repository")
        self.assertEqual(subsec.find("include").text, "SubSection include")
        self.assertEqual(len(subsec.findall("property")), 1)

        # Test absence of non-Section tags
        self.assertEqual(len(sec[1]), 1)
        self.assertEqual(len(sec[1].findall("name")), 1)

    def test_convert_odml_file_property(self):
        """Test proper conversion of the odml.Property entity from
        odml model version 1 to version 1.1.

        The test checks for the proper conversion of all valid
        Property tags and exclusion of non-Property tags.
        """

        doc = """
                <odML version="1">
                  <section>
                    <name>Valid Property tags test</name>
                    <property>
                      <name>Property name</name>
                      <type>Property type</type>
                      <definition>Property definition</definition>
                      <dependency>Property dependency</dependency>
                      <dependencyvalue>Property dependency value</dependencyvalue>
                    </property>
                  </section>

                  <section>
                    <name>Unsupported Property tags test</name>
                    <property>
                      <name>Invalid Property</name>
                      <invalid>Invalid tag</invalid>
                      <section><name>Invalid Section</name></section>
                    </property>
                    <property>Property with no name</property>
                  </section>
                </odML>
        """

        file = io.StringIO(unicode(doc))
        conv_doc = VC.convert_odml_file(file)
        root = conv_doc.getroot()
        sec = root.findall("section")

        # Test valid Property tags
        self.assertEqual(sec[0].find("name").text, "Valid Property tags test")
        self.assertEqual(len(sec[0].findall("property")), 1)
        prop = sec[0].find("property")
        self.assertEqual(len(prop), 5)
        self.assertEqual(prop.find("name").text, "Property name")
        self.assertEqual(prop.find("type").text, "Property type")
        self.assertEqual(prop.find("definition").text, "Property definition")
        self.assertEqual(prop.find("dependency").text, "Property dependency")
        self.assertEqual(prop.find("dependencyvalue").text, "Property dependency value")

        # Test non-import of Property w/o name
        self.assertEqual(len(sec[1].findall("property")), 1)
        # Test absence of non-Property tags
        prop = sec[1].find("property")
        self.assertEqual(len(prop), 1)
        self.assertEqual(len(prop.findall("name")), 1)
