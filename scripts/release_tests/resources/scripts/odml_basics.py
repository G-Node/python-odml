import sys
import unittest

try:
    # Test possible imports of all parsers without importing the full odML package
    from odml.tools import ODMLReader, ODMLWriter, RDFReader, RDFWriter
    from odml.tools.converters import FormatConverter, VersionConverter
    from odml.tools import XMLReader, XMLWriter, DictReader, DictWriter

    import odml
except Exception as exc:
    print("-- Failed on an import: %s" % exc)
    sys.exit(-1)


class TestODMLBasics(unittest.TestCase):

    def test_load(self):
        print("-- Load odml xml file")
        xdoc = odml.load('./load.odml.xml')
        print(xdoc.pprint())

        print("-- Load odml json file")
        jdoc = odml.load('./load.odml.json', 'JSON')
        self.assertEqual(xdoc, jdoc)

        print("-- Load odml yaml file")
        ydoc = odml.load('./load.odml.yaml', 'YAML')
        self.assertEqual(xdoc, ydoc)

        print("-- Document loading tests success")

    def test_version_load(self):
        print("-- Test invalid version exception xml file load")
        with self.assertRaises(odml.tools.parser_utils.InvalidVersionException):
            _ = odml.load('./load_v1.odml.xml')
        print("-- Invalid version loading test success")

    def test_tools_init(self):
        _ = ODMLReader()
        _ = ODMLWriter()
        _ = RDFReader()
        _ = RDFWriter([odml.Document()])
        _ = FormatConverter()
        _ = VersionConverter("/I/do/not/exist.txt")
        _ = XMLReader()
        _ = XMLWriter(odml.Document())
        _ = DictReader()
        _ = DictWriter()


if __name__ == "__main__":
    try:
        svi = sys.version_info
        print("-- Using Python '%s.%s.%s'" % (svi.major, svi.minor, svi.micro))
        print("-- Testing odml Version: '%s'" % odml.VERSION)

        unittest.main()

    except Exception as exc:
        print("-- Failed on a test: %s" % exc)
        sys.exit(-1)
