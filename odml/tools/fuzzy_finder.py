import re

from rdflib import Namespace, RDF
from rdflib.plugins.sparql import prepareQuery

from odml.format import Document
from odml.format import Property
from odml.format import Section


class FuzzyFinder(object):
    """ 
    Class for simplifying the creation of prepared SPARQL queries 
    
    Usage:
        q = "doc(author:D. N. Adams) section(name:Stimulus) prop(name:Contrast, value:20, unit:%)"
        prepared_query = FuzzyFinder().get_query(q)
    """
    def __init__(self):
        self.q_dict = {}
        self.query = ''

    def get_query(self, q_str):
        # TODO find out if the validation for the q_str is important
        # We can possibly warn about not used parts and print the parsed dictionary
        self._parse_query_string(q_str)
        self._prepare_query()
        q = prepareQuery(self.query, initNs={"odml": Namespace("https://g-node.org/projects/odml-rdf#"),
                                             "rdf": RDF})
        return q

    def _prepare_query(self):
        # TODO queries for multiple section included e.g. "sec(name:test1) sec(name:test2)"
        self.query += 'SELECT * WHERE {\n'

        doc_attrs = self.q_dict['Doc']
        if len(doc_attrs) > 0:
            self.query += '?d rdf:type odml:Document .\n'
            for i in doc_attrs:
                if len(i) > 2:
                    raise ValueError("Attributes in the query \"{}\" are not valid.".format(i))
                else:
                    attr = Document.rdf_map(i[0])
                    if attr:
                        self.query += '?d {0} \"{1}\" .\n'.format(re.sub("https://g-node.org/projects/odml-rdf#",
                                                                         "odml:", attr), i[1])

        sec_attrs = self.q_dict['Sec']
        if len(sec_attrs) > 0:
            self.query += '?d odml:hasSection ?s .\n' \
                          '?s rdf:type odml:Section .\n'
            for i in sec_attrs:
                if len(i) > 2:
                    raise ValueError("Attributes in the query \"{}\" are not valid.".format(i))
                else:
                    attr = Section.rdf_map(i[0])
                    if attr:
                        self.query += '?s {0} \"{1}\" .\n'.format(re.sub("https://g-node.org/projects/odml-rdf#",
                                                                         "odml:", attr), i[1])

        prop_attrs = self.q_dict['Prop']
        if len(prop_attrs) > 0:
            self.query += '?s odml:hasProperty ?p .\n' \
                          '?p rdf:type odml:Property .\n'
            for i in prop_attrs:
                if len(i) > 2:
                    raise ValueError("Attributes in the query \"{}\" are not valid.".format(i))
                elif i[0] == 'value':
                    values = i[1]
                    if values:
                        self.query += "?p odml:hasValue ?v .\n?v rdf:type rdf:Bag .\n"
                        for v in values:
                            self.query += '?v rdf:li \"{}\" .\n'.format(v)
                else:
                    attr = Property.rdf_map(i[0])
                    if attr:
                        self.query += '?p {0} \"{1}\" .\n'.format(re.sub("https://g-node.org/projects/odml-rdf#",
                                                                         "odml:", attr), i[1])

        self.query += '}'

    def _parse_query_string(self, q_str):
        doc_pattern = re.compile("(doc|document)\(.*?\)")
        self._parse_doc(re.search(doc_pattern, q_str))

        sec_pattern = re.compile("(sec|section)\(.*?\)")
        self._parse_sec(re.search(sec_pattern, q_str))
        print(re.search(sec_pattern, q_str))

        prop_pattern = re.compile("(prop|property)\(.*?\)")
        self._parse_prop(re.search(prop_pattern, q_str))

    def _parse_doc(self, doc):
        p = re.compile("(id|author|date|version|repository|sections):(.*?)[,|\)]")
        self.q_dict['Doc'] = re.findall(p, doc.group(0))

    def _parse_sec(self, sec):
        p = re.compile("(id|name|definition|type|repository|reference|sections|properties):(.*?)[,|\)]")
        self.q_dict['Sec'] = re.findall(p, sec.group(0))
        print("sec sdfds ", re.findall(p, sec.group(0)))

    def _parse_prop(self, prop):
        p = re.compile("(id|name|definition|dtype|unit|uncertainty|reference|value_origin):(.*?)[,|\)]")
        self.q_dict['Prop'] = re.findall(p, prop.group(0))

        p_value = re.compile("value:\[(.*)]")
        value_group = re.findall(p_value, prop.group(0))
        if value_group:
            values = re.split(", ?", value_group[0])
            self.q_dict['Prop'].append(('value', values))
