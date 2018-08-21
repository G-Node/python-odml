"""odmlExportRDF

odmlExportRDF searches for odML files within a provided SEARCHDIR
and converts them to the newest odML format version and
exports all found and resulting odML files to XML formatted RDF.
Original files will never be overwritten.

Usage: odmlexportrdf [-r] [-o OUT] SEARCHDIR

Arguments:
    SEARCHDIR       Directory to search for odML files.

Options:
    -o OUT          Output directory. Must exist if specified.
                    If not specified, output files will be
                    written to the current directory.
    -r              Search recursively.
    -h --help       Show this screen.
    --version       Show version.
"""

import os
import pathlib
import sys
import tempfile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import odml

from docopt import docopt
from odml.tools.odmlparser import ODMLReader, ODMLWriter
from odml.tools.version_converter import VersionConverter as VerConf

try:
    unicode = unicode
except NameError:
    unicode = str


def run_rdf_export(odml_file, export_dir):
    """
    Convert an odML file to an XML RDF file and
    export it to an export directory with the
    same name as the original file and a '.rdf' file
    ending.
    :param odml_file: odML file to be converted to RDF.
    :param export_dir:
    """
    out_name = os.path.splitext(os.path.basename(odml_file))[0]
    out_file = os.path.join(export_dir, "%s.rdf" % out_name)
    doc = ODMLReader().from_file(odml_file)
    ODMLWriter("RDF").write_file(doc, out_file)


def run_conversion(file_list, output_dir, rdf_dir, report, source_format="XML"):
    """
    Convert a list of odML files to the latest odML version if required
    and export all files to XML RDF files in a specified output directory.
    :param file_list: list of files to be exported to RDF.
    :param output_dir: Directory where odML files converted to
                       the latest odML version will be saved.
    :param rdf_dir: Directory where exported RDF files will be saved.
    :param report: Reporting StringIO.
    :param source_format: Original file format of the odML source files.
                          XML, JSON and YAML are supported, default is XML.
    """
    # Exceptions are kept as broad as possible to ignore any non-odML or
    # invalid odML files and ensuring everything that can be will be converted.
    for curr_file in file_list:
        file_path = unicode(curr_file.absolute())
        report.write("[Info] Handling file '%s'\n" % file_path)
        # When loading the current file succeeds, it is
        # a recent odML format file and can be exported
        # to RDF right away. Otherwise it needs to be
        # converted to the latest odML version first.
        try:
            odml.load(file_path, source_format)
            report.write("[Info] RDF conversion of '%s'\n" % file_path)
            run_rdf_export(file_path, rdf_dir)
        except Exception as exc:
            out_name = os.path.splitext(os.path.basename(file_path))[0]
            outfile = os.path.join(output_dir, "%s_conv.xml" % out_name)
            try:
                VerConf(file_path).write_to_file(outfile, source_format)
                try:
                    report.write("[Info] RDF conversion of '%s'\n" % outfile)
                    run_rdf_export(outfile, rdf_dir)
                except Exception as exc:
                    report.write("[Error] converting '%s' to RDF: '%s'\n" %
                                 (file_path, exc))
            except Exception as exc:
                # Ignore files we cannot parse or convert
                report.write("[Error] version converting file '%s': '%s'\n" %
                             (file_path, exc))


def main(args=None):
    """
    Convenience script to automatically convert odML files
    within a directory (tree) to RDF. Check the cli help
    for details.
    :param args: Command line arguments
    """
    parser = docopt(__doc__, argv=args, version="0.1.0")

    root = parser['SEARCHDIR']
    if not os.path.isdir(root):
        print(docopt(__doc__, "-h"))
        exit(1)

    # Handle all supported odML file formats.
    if parser['-r']:
        xfiles = list(pathlib.Path(root).rglob('*.odml'))
        xfiles.extend(list(pathlib.Path(root).rglob('*.xml')))
        jfiles = list(pathlib.Path(root).rglob('*.json'))
        yfiles = list(pathlib.Path(root).rglob('*.yaml'))
    else:
        xfiles = list(pathlib.Path(root).glob('*.odml'))
        xfiles.extend(list(pathlib.Path(root).glob('*.xml')))
        jfiles = list(pathlib.Path(root).glob('*.json'))
        yfiles = list(pathlib.Path(root).glob('*.yaml'))

    out_root = os.getcwd()
    if parser["-o"]:
        if not os.path.isdir(parser["-o"]):
            print("[Error] Could not find output directory '%s'" % parser["-o"])
            exit(1)

        out_root = parser["-o"]

    out_dir = tempfile.mkdtemp(prefix="odmlconv_", dir=out_root)
    rdf_dir = tempfile.mkdtemp(prefix="odmlrdf_", dir=out_dir)

    # Use this monkeypatch reporter until there is a way
    # to run the converters silently.
    report = StringIO()
    report.write("[Info] Files will be saved to '%s'\n" % out_dir)

    run_conversion(xfiles, out_dir, rdf_dir, report)
    run_conversion(jfiles, out_dir, rdf_dir, report, "JSON")
    run_conversion(yfiles, out_dir, rdf_dir, report, "YAML")

    print(report.getvalue())
    report.close()


if __name__ == "__main__":
    main(sys.argv[1:])
