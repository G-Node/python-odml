import os
import re
import sys

from lxml import etree as ET

import odml

try:
    unicode = unicode
except NameError:
    unicode = str


class VersionConverter:
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

    @staticmethod
    def convert_odml_file(filename):
        """
        Converts a given file to the odml version 1.1.
        Unites multuple value objects and brings value attributes out of the <value> tag
        """
        tree = None
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            VersionConverter.validate_xml(filename)
            tree = ET.parse(filename)
            tree = VersionConverter._replace_same_name_entities(tree)
            root = tree.getroot()
            root.set("version", "1.1")
            for prop in root.iter("property"):
                one_value = True
                first_value = None
                for value in prop.iter("value"):
                    if one_value:
                        first_value = value
                        for val_elem in value.iter():
                            if val_elem.tag != "value" and one_value:
                                elem_name = VersionConverter._version_map[val_elem.tag] \
                                    if val_elem.tag in VersionConverter._version_map else val_elem.tag
                                new_elem = ET.Element(elem_name)
                                new_elem.text = val_elem.text
                                value.getparent().append(new_elem)  # appending to the property
                                value.remove(val_elem) 
                        one_value = False
                    else:
                        first_value.text += ", " + value.text
                        prop.remove(value)
        return tree

    @staticmethod
    def validate_xml(filename):
        """
        Fix an xml file by deleting known mismatching tags 
        """
        changes_list = []
        with open(filename) as f:
            doc = f.read()
            for k, v in VersionConverter._error_strings.items():
                if k not in doc:
                    continue
                else:
                    changes_list.append(k)

        if len(changes_list) == 0:
            return

        # Write the changed content, if found in the file
        with open(filename, 'w') as f:
            for str in changes_list:
                doc = doc.replace(str, VersionConverter._error_strings[str])
            f.write(doc)

    @staticmethod
    def _replace_same_name_entities(tree):
        """
        Changes same section names in the doc by adding <-{index}> to the next section occurrences
        :param tree: ElementTree of the doc
        :return: ElementTree
        """
        section_map = {}
        root = tree.getroot()
        for section in root.iter("section"):
            n = section.find("name")
            if n.text not in section_map:
                section_map[n.text] = 1
            else:
                section_map[n.text] += 1
                n.text += "-" + str(section_map[n.text])
        return tree

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
            print("Empty file: ", filename)


class DirectoryParser:
    def __init__(self):
        self.doc = None

    def convert_directory(self, directory_path, suffix, extension):
        """
        For given directory with mostly odml files in the xml format creates folders with converted to the version 1.1
        .xml files and .odml files respectively. The directory can contain subdirectories. For each subdirectory result 
        folder will be created.
        :param directory_path: path to root folder
        :param suffix: the suffix which is added to the name of the new directory with converted files
        :param extension: the format to which we convert files from the directory_path (.xml or .odml)
                          .odml files can be created only from previously converted xmls
        Example:
        For given ./gin_files repo
            - gin_files
                - drosophila
                    - 1.xml
                    - 2.xml
                - spike_lfp
                    - metadata-date.xml
        
        DirectoryParser().convert_directory("./gin_files/", "_updated", ".xml") command will add
            - gin_files
                - drosophila
                    - 1.xml
                    - 2.xml
                - drosophila_updated
                    - 2.xml
                - spike_lfp
                    - metadata-date.xml
                - spike_lfp_updated
                    - metadata-date.xml
        
        DirectoryParser().convert_directory("./gin_files/", "_odmls", ".odml") consecutive
                - drosophila
                    - 2.xml
                - drosophila_updated
                    - 2.xml
                - drosophila_updated_odmls
                    - 2.odml
                - spike_lfp
                    - metadata-date.xml
                - spike_lfp_updated
                    - metadata-date.xml
                - spike_lfp_updated_odmls
                    - metadata-date.odml
                    
        """
        for dir_path, dir_names, file_names in os.walk(directory_path):
            for file_name in file_names:
                if ("_updated" or "_odmls") not in dir_path and extension == ".xml":
                    file_path = os.path.join(dir_path, file_name)
                    if file_path.endswith('.xml') or file_path.endswith('.xml'):
                        original_file = file_path
                        # get the last directory name in path
                        root = re.sub(r"/[a-z0-9_%-]*\.[a-z]*", r"/", file_path)
                        directory_name = os.path.basename(os.path.normpath(root))
                        # create path to the new file in the new directory
                        file_path = re.sub(r"/"+directory_name, r"/"+directory_name+suffix, file_path)
                        self._create_sub_directory(file_path)
                        VersionConverter(original_file).write_to_file(file_path)
                # converting validated xmls in "./{directory}_updated
                elif "_updated" in dir_path and extension == ".odml":
                    file_path = os.path.join(dir_path, file_name)
                    if file_path.endswith('.xml') or file_path.endswith('.xml'):
                        print(file_path)
                        self.doc = odml.load(file_path)
                        # change extension to .odml
                        file_path = re.sub(r"\.(xml|json)", ".odml", file_path)
                        root = re.sub(r"/[a-z0-9_%-]*\.[a-z]*", r"/", file_path)
                        directory_name = os.path.basename(os.path.normpath(root))
                        file_path = re.sub(r"/"+directory_name, r"/"+directory_name+suffix, file_path)
                        self._create_sub_directory(file_path)
                        odml.save(self.doc, file_path)

    def _create_sub_directory(self, new_file_path):
        """
        Creates the new directory to store the converted file
        Example:
            ./folder/file.xml -> ./folder_odmls/file.odml
        """
        root = re.sub(r"/[a-z0-9_%-]*\.[a-z]*", r"/", new_file_path)
        if not os.path.isdir(root):
            os.makedirs(root)