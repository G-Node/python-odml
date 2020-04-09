"""
The FormatConverter can be used from the command line and within scripts
to convert between the different odML formats and update previous file format
versions to the most recent one.

A full list of the available odML output formats is available via the
CONVERSION_FORMATS constant.

Command line usage:
python -m <in_dir> <odml_out_format> [-out <out_dir>] [-r]

Examples:
1) >> python -m odml.tools.converters.format_converter <in_dir> v1_1 -out <out_dir> -r

    Convert files from the path <in_dir> to .xml odml version 1.1, writes them
    to <out_dir> including subdirectories and its files from the input path.

2) >> python -m odml.tools.converters.format_converter <in_dir> odml

    Converts files from path <in_dir> to .odml and writes them
    to <in_dir_odml> not including subdirectories.
"""

import argparse
import copy
import os
import re
import sys

import odml

from .. import RDFWriter
from . import VersionConverter
from ..parser_utils import RDF_CONVERSION_FORMATS

try:
    unicode = unicode
except NameError:
    unicode = str


CONVERSION_FORMATS = copy.deepcopy(RDF_CONVERSION_FORMATS)
CONVERSION_FORMATS.update({
    'v1_1': '.xml',
    'odml': '.odml'
})


class FormatConverter(object):
    """
    Class for converting between the different odML file formats.
    """

    @classmethod
    def convert(cls, args=None):
        """
        Enables usage of the argparse for calling convert_dir(...)

        Usage:
        python -m <in_dir> <odml_out_format> [-out <out_dir>] [-r]

        Examples:
          1) >> python -m odml.tools.converters.format_converter <in_dir> v1_1 -out <out_dir> -r
            Convert files from the path <in_dir> to .xml odml version 1.1, writes them
            to <out_dir> including subdirectories and its files from the input path.

          2) >> python -m odml.tools.converters.format_converter <in_dir> odml
            Converts files from path <in_dir> to .odml and writes them
            to <in_dir_odml> not including subdirectories.

        :param args: Command line arguments. See usage for details.
        """
        desc = "Convert directory with odml files to another format"
        parser = argparse.ArgumentParser(description=desc)
        parser.add_argument("input_dir", help="Path to input directory")
        parser.add_argument("result_format", choices=list(CONVERSION_FORMATS),
                            help="Format of output files")
        parser.add_argument("-out", "--output_dir", help="Path for output directory")
        parser.add_argument("-r", "--recursive", action="store_true",
                            help="Enable converting files from subdirectories")
        args = parser.parse_args(args)
        recursive = bool(args.recursive)
        cls.convert_dir(args.input_dir, args.output_dir, recursive, args.result_format)

    @classmethod
    def convert_dir(cls, input_dir, output_dir, parse_subdirs, res_format):
        """
        Convert files from given input directory to the specified res_format.

        :param input_dir: Path to input directory
        :param output_dir: Path for output directory.
                           If None, new directory will be created on the same level as input
        :param parse_subdirs: If True enable converting files from subdirectories
        :param res_format: Format of output files.
                           Possible choices: "v1_1" (version 1 to version 1.1 xml files)
                                             "odml" (version 1.1 .xml to .odml files)
                                             "turtle", "nt" etc. (version 1.1 to RDF files)
                                             (full list of RDF serializers in CONVERSION_FORMATS)
        """
        if res_format not in CONVERSION_FORMATS:
            raise ValueError("Format for output files is incorrect. "
                             "Please choose from the list: {}".format(list(CONVERSION_FORMATS)))

        cls._check_input_output_directory(input_dir, output_dir)
        input_dir = os.path.join(input_dir, '')

        if output_dir is None:
            # find the directory that contains input_dir
            input_dir_name = os.path.basename(os.path.dirname(input_dir))
            root_dir = os.path.dirname(os.path.dirname(input_dir))
            output_dir_name = input_dir_name + "_" + res_format
            output_dir = os.path.join(root_dir, output_dir_name)
            cls._create_sub_directory(output_dir)

        output_dir = os.path.join(output_dir, '')

        if not parse_subdirs:
            for file_name in os.listdir(input_dir):
                if os.path.isfile(os.path.join(input_dir, file_name)):
                    cls._convert_file(os.path.join(input_dir, file_name),
                                      os.path.join(output_dir, file_name), res_format)
        else:
            for dir_path, _, file_names in os.walk(input_dir):
                for file_name in file_names:
                    in_file_path = os.path.join(dir_path, file_name)
                    out_dir = re.sub(r"" + input_dir, r"" + output_dir, dir_path)
                    out_file_path = os.path.join(out_dir, file_name)
                    cls._create_sub_directory(out_dir)
                    cls._convert_file(in_file_path, out_file_path, res_format)

    @classmethod
    def _convert_file(cls, input_path, output_path, res_format):
        """
        Converts a file from given input_path to res_format. Will raise a ValueError
        if the provided output format (res_format) is not supported.

        :param input_path: full path including file name of the file to be converted.
        :param output_path: full path including file name of the output file.
                            If required the file extension will be adjusted to the
                            output format.
        :param res_format: Format the input file will be converted to. Only formats
                           listed in constant CONVERSION_FORMATS are supported.
        """
        if res_format == "v1_1":
            VersionConverter(input_path).write_to_file(output_path)
        elif res_format == "odml":
            if not output_path.endswith(".odml"):
                file_path, _ = os.path.splitext(output_path)
                output_path = file_path + ".odml"
            odml.save(odml.load(input_path), output_path)
        elif res_format in CONVERSION_FORMATS:
            if not output_path.endswith(CONVERSION_FORMATS[res_format]):
                file_path, _ = os.path.splitext(output_path)
                output_path = file_path + CONVERSION_FORMATS[res_format]
            RDFWriter(odml.load(input_path)).write_file(output_path, res_format)
        else:
            raise ValueError("Format for output files is incorrect. "
                             "Please choose from the list: {}".format(list(CONVERSION_FORMATS)))

    @staticmethod
    def _create_sub_directory(dir_path):
        """
        Creates a new directory if it does not yet exist.

        :param dir_path: path of the required directory.
        """
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

    @staticmethod
    def _check_input_output_directory(input_dir, output_dir):
        """
        Checks if the provided directories are valid. Will raise a ValueError
        if the directories do not exist.

        :param input_dir: input file directory.
        :param output_dir: output file directory. Can be None.
        """
        if not input_dir or not os.path.isdir(input_dir):
            raise ValueError("The path to input directory is not a valid path")

        if output_dir is not None and not os.path.isdir(output_dir):
            raise ValueError("The path to output directory is not a valid path")

        if not output_dir:
            if os.path.dirname(input_dir) == input_dir:
                msg = "Cannot write to %s. Please specify an output directory" % input_dir
                raise ValueError(msg)


if __name__ == "__main__":
    FormatConverter.convert(sys.argv[1:])
