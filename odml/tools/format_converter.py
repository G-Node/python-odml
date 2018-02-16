import argparse
import os
import re
import sys

import odml
from .rdf_converter import RDFWriter
from .version_converter import VersionConverter

try:
    unicode = unicode
except NameError:
    unicode = str


class FormatConverter(object):

    _conversion_formats = {
        'v1_1': '.xml',
        'odml': '.odml',
        # rdflib version "4.2.2" serialization formats
        'xml': '.rdf',
        'pretty-xml': '.rdf',
        'trix': '.rdf',
        'n3': '.n3',
        'turtle': '.ttl',
        'ttl': '.ttl',
        'ntriples': '.nt',
        'nt': '.nt',
        'nt11': '.nt',
        'trig': '.trig',
        'json-ld': '.jsonld'
    }

    @classmethod
    def convert(cls, args=None):
        """
        Enable usage of the argparse for calling convert_dir(...)
        Example:
            1) >> python format_converter.py ./..path../input_dir v1_1 -out ./..path../output_dir -r
            
               Convert files from the path <./..path../input_dir> to .xml odml version 1.1,
               writes them into <./..path../output_dir> including subdirectories 
               and its files from the input path.
            
            2) >> python format_converter.py ./..path../input_dir odml
            
               Converts files from path <./..path../input_dir> to .odml,
               writes them into <./..path../input_dir_odml> not including subdirectories.
        """
        parser = argparse.ArgumentParser(description="Convert directory with odml files to another format")
        parser.add_argument("input_dir", help="Path to input directory")
        parser.add_argument("result_format", choices=list(cls._conversion_formats),
                            help="Format of output files")
        parser.add_argument("-out", "--output_dir", help="Path for output directory")
        parser.add_argument("-r", "--recursive", action="store_true",
                            help="Enable converting files from subdirectories")
        args = parser.parse_args(args)
        r = True if args.recursive else False
        cls.convert_dir(args.input_dir, args.output_dir, r, args.result_format)

    @classmethod
    def convert_dir(cls, input_dir, output_dir, parse_subdirs, res_format):
        """
        Convert files from given input directory to the specified res_format.
        :param input_dir: Path to input directory
        :param output_dir: Path for output directory. If None, new directory will be created on the same level as input
        :param parse_subdirs: If True enable converting files from subdirectories
        :param res_format: Format of output files. 
                           Possible choices: "v1_1" (converts to version 1.1 from version 1 xml)
                                             "odml" (converts to .odml from version 1.1 .xml files)
                                             "turtle", "nt" etc. (converts to rdf formats from version 1.1 .odml files)
                                             (see full list of rdf serializers in FormatConverter._conversion_formats)
        """
        if res_format not in cls._conversion_formats:
            raise ValueError("Format for output files is incorrect. "
                             "Please choose from the list: {}".format(cls._conversion_formats.keys()))

        cls._check_input_output_directory(input_dir, output_dir)
        input_dir = os.path.join(input_dir, '')

        if output_dir is None:
            input_dir_name = os.path.basename(os.path.dirname(input_dir))
            root_dir = os.path.dirname(os.path.dirname(input_dir))  # find the directory that contains input_dir
            output_dir_name = input_dir_name + "_" + res_format
            output_dir = os.path.join(root_dir, output_dir_name)
            cls._create_sub_directory(output_dir)

        output_dir = os.path.join(output_dir, '')

        if not parse_subdirs:
            for file_name in os.listdir(input_dir):
                if os.path.isfile(os.path.join(input_dir, file_name)):
                    cls._convert_file(os.path.join(input_dir, file_name), os.path.join(output_dir, file_name),
                                      res_format)
        else:
            for dir_path, dir_names, file_names in os.walk(input_dir):
                for file_name in file_names:
                    in_file_path = os.path.join(dir_path, file_name)
                    out_dir = re.sub(r"" + input_dir, r"" + output_dir, dir_path)
                    out_file_path = os.path.join(out_dir, file_name)
                    cls._create_sub_directory(out_dir)
                    cls._convert_file(in_file_path, out_file_path, res_format)

    @classmethod
    def _convert_file(cls, input_path, output_path, res_format):
        """
        Convert a file from given input_path to res_format.
        """
        if res_format == "v1_1":
            VersionConverter(input_path).write_to_file(output_path)
        elif res_format == "odml":
            if not output_path.endswith(".odml"):
                p, _ = os.path.splitext(output_path)
                output_path = p + ".odml"
            odml.save(odml.load(input_path), output_path)
        elif res_format in cls._conversion_formats:
            if not output_path.endswith(cls._conversion_formats[res_format]):
                p, _ = os.path.splitext(output_path)
                output_path = p + cls._conversion_formats[res_format]
            RDFWriter(odml.load(input_path)).write_file(output_path, res_format)

    @staticmethod
    def _create_sub_directory(dir_path):
        """
        Creates the new directory to store the converted file.
        """
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

    @staticmethod
    def _check_input_output_directory(input_dir, output_dir):
        """
        Checks if provided directory is valid - not None, is directory and not a root folder in the File System 
        if output dir was not provided.
        Raise relevant exceptions.
        """
        if not input_dir or not os.path.isdir(input_dir):
            raise ValueError("The path to input directory is not a valid path")

        if output_dir is not None and not os.path.isdir(output_dir):
            raise ValueError("The path to output directory is not a valid path")

        if not output_dir:
            if os.path.dirname(input_dir) == input_dir:
                raise ValueError("The input directory cannot be a root folder of the File System if "
                                 "output directory was not specified")

if __name__ == "__main__":
    FormatConverter.convert(sys.argv[1:])
