import argparse
import io
import os
import re
import sys

from lxml import etree as ET

import odml
from odml.tools.xmlparser import XML_VERSION

try:
    unicode = unicode
except NameError:
    unicode = str


class VersionConverter(object):
    """
    Class for converting odml xml files from version 1.0 to 1.1
    """
    header = """<?xml version="1.0" encoding="UTF-8"?>\n"""

    _version_map = {
        'type': 'type'
    }

    _error_strings = {
        '<B0>': ''
    }

    def __init__(self, filename):
        self.filename = filename

    @classmethod
    def convert_odml_file(cls, filename):
        """
        Converts a given file to the odml version 1.1.
        Unites multuple value objects and brings value attributes out of the <value> tag.
        :param filename: The path to the file or io.StringIO object
        """
        tree = None
        if isinstance(filename, io.StringIO):
            cls._fix_unmatching_tags(filename)
            tree = ET.ElementTree(ET.fromstring(filename.getvalue()))
        elif os.path.exists(filename) and os.path.getsize(filename) > 0:
            cls._fix_unmatching_tags(filename)
            tree = ET.parse(filename)
        else:
            raise ValueError("The filename is not a valid path nor io.StringIO object")

        tree = cls._replace_same_name_entities(tree)
        root = tree.getroot()
        root.set("version", XML_VERSION)
        for prop in root.iter("property"):
            one_value = True
            first_value = None
            for value in prop.iter("value"):
                if one_value:
                    first_value = value
                    for val_elem in value.iter():
                        if val_elem.tag != "value" and one_value:
                            elem_name = cls._version_map[val_elem.tag] \
                                if val_elem.tag in cls._version_map else val_elem.tag
                            new_elem = ET.Element(elem_name)
                            new_elem.text = val_elem.text
                            value.getparent().append(new_elem)  # appending to the property
                            value.remove(val_elem)
                    one_value = False
                else:
                    first_value.text += ", " + value.text
                    prop.remove(value)
        return tree

    @classmethod
    def _fix_unmatching_tags(cls, filename):
        """
        Fix an xml file by deleting known mismatching tags.
        :param filename: The path to the file or io.StringIO object
        """
        changes = False
        if isinstance(filename, io.StringIO):
            doc = filename.getvalue()
        elif os.path.exists(filename) and os.path.getsize(filename) > 0:
            f = open(filename, 'r+')
            doc = f.read()
        for k, v in cls._error_strings.items():
            if k in doc:
                doc = doc.replace(k, cls._error_strings[k])
                changes = True

        if changes:
            if isinstance(filename, io.StringIO):
                return io.StringIO(doc)
            else:
                f.truncate(0)
                f.write(doc)
                f.close()

    @classmethod
    def _replace_same_name_entities(cls, tree):
        """
        Changes same section names in the doc by adding <-{index}> to the next section occurrences.
        :param tree: ElementTree of the doc
        :return: ElementTree
        """
        sec_map = {}
        prop_map = {}
        root = tree.getroot()
        for sec in root.iter("section"):
            n = sec.find("name")
            if n is not None:
                cls._change_entity_name(sec_map, n)
            else:
                raise Exception("Section attribute name is not specified")
            for prop in sec.iter("property"):
                if prop.getparent() == sec:
                    n = prop.find("name")
                    if n is not None:
                        cls._change_entity_name(prop_map, n)
            prop_map.clear()
        return tree

    @staticmethod
    def _change_entity_name(elem_map, name):
        if name.text not in elem_map:
            elem_map[name.text] = 1
        else:
            elem_map[name.text] += 1
            name.text += "-" + str(elem_map[name.text])

    def __str__(self):
        tree = self.convert_odml_file(self.filename)
        return ET.tounicode(tree, pretty_print=True) if tree else ""

    def __unicode__(self):
        tree = self.convert_odml_file(self.filename)
        return ET.tounicode(tree, pretty_print=True) if tree else ""
    
    def write_to_file(self, filename):
        if sys.version_info < (3,):
            data = unicode(self).encode('utf-8')
        else:
            data = str(self)
        if data and "<odML " in data:
            f = open(filename, "w")
            f.write(self.header)
            f.write(data)
            f.close()
        else:
            print("Not an odml file: ", filename)


class FormatConverter(object):

    _conversion_formats = [
        "v1_1",
        "odml"
    ]

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
        parser.add_argument("result_format", choices=['v1_1', 'odml'], help="Format of output files")
        parser.add_argument("-out", "--output_dir", help="Path for output directory")
        parser.add_argument("-r", "--recursive", action="store_true", help="Enable converting files from subdirectories")
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
        """
        if res_format not in cls._conversion_formats:
            raise ValueError("Format for output files is incorrect. "
                             "Please choose from the list: {}".format(cls._conversion_formats))

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
                    cls._convert_file(os.path.join(input_dir, file_name), os.path.join(output_dir, file_name), res_format)
        else:
            for dir_path, dir_names, file_names in os.walk(input_dir):
                for file_name in file_names:
                    in_file_path = os.path.join(dir_path, file_name)
                    out_dir = re.sub(r"" + input_dir, r"" + output_dir, dir_path)
                    out_file_path = os.path.join(out_dir, file_name)
                    cls._create_sub_directory(out_dir)
                    cls._convert_file(in_file_path, out_file_path, res_format)

    @staticmethod
    def _convert_file(input_path, output_path, res_format):
        """
        Convert a file from given input_path to res_format.
        """
        if res_format == "v1_1":
            VersionConverter(input_path).write_to_file(output_path)
        elif res_format == "odml":
            if output_path.endswith(".xml"):
                p, _ = os.path.splitext(output_path)
                output_path = p + ".odml"
            odml.save(odml.load(input_path), output_path)
        else:
            # TODO implement conversion to rdfs, json etc.
            # Discuss how exceptions can be managed:
            # 1) Ignore not valid files (no way to convert from xml to rdf, or version1 xml to odml)
            # Warn about about ignored files.
            # 2) Run converting functions if problems detected and only then warn.
            return

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
