import re

from rdflib import Namespace, RDF
from rdflib.plugins.sparql import prepareQuery

from odml.format import Document
from odml.format import Property
from odml.format import Section


class QueryCreator(object):
    """ 
    Class for simplifying the creation of prepared SPARQL queries 
    
    Usage:
        q = "doc(author:D. N. Adams) section(name:Stimulus) prop(name:Contrast, value:20, unit:%)"
        prepared_query = QueryCreator().get_query(q)
    """
    possible_query_variables = {'d': 'Document', 's': 'Section',
                                'p': 'Property', 'v': 'Bag URI', 'value': 'Value'}

    possible_q_dict_keys = ['Doc', 'Sec', 'Prop']

    def __init__(self, q_dict=None):
        """
        :param q_dict: dictionary with query parameters
                       Example: {'Sec': [('name', 'some_name'), ('type', 'Stimulus')],
                                 'Doc': [('author': 'Adams')]}
        """
        self.q_dict = q_dict if q_dict else {}
        self.query = ''

    def get_query(self, q_str):
        # TODO find out if the validation for the q_str is important
        # We can possibly warn about not used parts and print the parsed dictionary
        self.parse_query_string(q_str)
        self.prepare_query()
        q = prepareQuery(self.query, initNs={"odml": Namespace("https://g-node.org/projects/odml-rdf#"),
                                             "rdf": RDF})
        return q

    def prepare_query(self):
        # TODO queries for multiple section included e.g. "sec(name:test1) sec(name:test2)"
        self.query += 'SELECT * WHERE {\n'

        if 'Doc' in self.q_dict.keys():
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
        if 'Sec' in self.q_dict.keys():
            print(self.q_dict)
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
        if 'Prop' in self.q_dict.keys():
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

        self.query += '}\n'
        return self.query

    def parse_query_string(self, q_str):
        doc_pattern = re.compile("(doc|document)\(.*?\)")
        doc = re.search(doc_pattern, q_str)
        if doc:
            self._parse_doc(doc)

        sec_pattern = re.compile("(sec|section)\(.*?\)")
        sec = re.search(sec_pattern, q_str)
        if sec:
            self._parse_sec(sec)

        prop_pattern = re.compile("((prop|property)\(.*?\))")
        prop = re.search(prop_pattern, q_str)
        if prop:
            self._parse_prop(prop)

    def _parse_doc(self, doc):
        p = re.compile("(id|author|date|version|repository|sections):(.*?)[,|\)]")
        if doc is not None:
            self.q_dict['Doc'] = re.findall(p, doc.group(0))

    def _parse_sec(self, sec):
        p = re.compile("(id|name|definition|type|repository|reference|sections|properties):(.*?)[,|\)]")
        if sec:
            self.q_dict['Sec'] = re.findall(p, sec.group(0))

    def _parse_prop(self, prop):
        p = re.compile("(id|name|definition|dtype|unit|uncertainty|reference|value_origin):(.*?)[,|\)]")
        if prop:
            self.q_dict['Prop'] = re.findall(p, prop.group(0))

            p_value = re.compile("value:\[(.*)]")

            value_group = re.findall(p_value, prop.group(0))
            if value_group:
                values = re.split(", ?", value_group[0])
                self.q_dict['Prop'].append(('value', values))
