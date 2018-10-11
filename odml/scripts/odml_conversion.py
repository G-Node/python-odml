"""odmlConversion

odmlConversion searches for odML files within a provided SEARCHDIR
and converts them to the newest odML format version.
Original files will never be overwritten. New files will be
written either to a new directory at the current or a specified
location.

Usage: odmlconversion [-r] [-o OUT] SEARCHDIR

Arguments:
    SEARCHDIR       Directory to search for odML files.

Options:
    -o OUT          Output directory. Must exist if specified.
                    If not specified, output files will be
                    written to the current directory.
    -r              Search recursively. Directory structures
                    will not be retained.
    -h --help       Show this screen.
    --version       Show version.
"""

import os
import pathlib
import sys
import tempfile

from docopt import docopt

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import odml

from odml.tools.version_converter import VersionConverter as VerConf

try:
    unicode = unicode
except NameError:
    unicode = str


def run_conversion(file_list, output_dir, report, source_format="XML"):
    """
    Convert a list of odML files to the latest odML version.
    :param file_list: list of files to be converted.
    :param output_dir: Directory where odML files converted to
                       the latest odML version will be saved.
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
        # a recent odML format file and can be ignored.
        try:
            odml.load(file_path, source_format)
            report.write("[Info] Skip recent version file '%s'" % file_path)
        except Exception as exc:
            out_name = os.path.splitext(os.path.basename(file_path))[0]
            outfile = os.path.join(output_dir, "%s_conv.xml" % out_name)
            try:
                VerConf(file_path).write_to_file(outfile, source_format)
            except Exception as exc:
                # Ignore files we cannot parse or convert
                report.write("[Error] version converting file '%s': '%s'\n" %
                             (file_path, exc))


def main(args=None):
    """
    Convenience script to automatically convert odML files
    within a directory (tree) to the newest file version.
    Check the cli help for details.
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

    # Use this monkeypatch reporter until there is a way
    # to run the converters silently.
    report = StringIO()
    report.write("[Info] Files will be saved to '%s'\n" % out_dir)

    run_conversion(xfiles, out_dir, report)
    run_conversion(jfiles, out_dir, report, "JSON")
    run_conversion(yfiles, out_dir, report, "YAML")

    print(report.getvalue())
    report.close()


if __name__ == "__main__":
    main(sys.argv[1:])
