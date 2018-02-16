import re
from abc import ABCMeta, abstractmethod

from rdflib import Namespace, RDF
from rdflib.plugins.sparql import prepareQuery

from ..format import Document
from ..format import Property
from ..format import Section


class BaseQueryCreator:

    __metaclass__ = ABCMeta

    possible_query_variables = {'d': 'Document', 's': 'Section',
                                'p': 'Property', 'v': 'Bag URI', 'value': 'Value'}

    possible_q_dict_keys = ['Doc', 'Sec', 'Prop']

    def __init__(self, q_dict=None):
        """
        :param q_dict: dictionary with query parameters
        """
        self.q_dict = q_dict if q_dict else {}
        self.query = ''
        super(BaseQueryCreator, self).__init__()

    @abstractmethod
    def get_query(self, q_str, q_parser):
        pass
    
    @abstractmethod
    def _prepare_query(self):
        pass


class BaseQueryParser:

    __metaclass__ = ABCMeta

    def __init__(self):
        self.q_dict = {}

    @abstractmethod
    def parse_query_string(self, q_str):
        pass


class QueryParserFuzzy(BaseQueryParser):

    def __init__(self):
        super(QueryParserFuzzy, self).__init__()

    def parse_query_string(self, q_str):
        """
        Parse query string and returns dict object with parameters.
        :param q_str: query string.
                      Example: FIND sec(name, type) prop(type) HAVING Stimulus, Contrast
        :return: dict object.
                 Example: {'Sec': ['name', 'type'],
                           'Doc': ['author'],
                           'Search': ['Stimulus', 'Contrast']}
        """
        self.q_dict = {}
        find_pattern = re.compile("FIND(.*?)HAVING")
        find_group = re.search(find_pattern, q_str).group(1).strip()
        if find_group:
            self._parse_find(find_group)

        having_pattern = re.compile("HAVING(.*)")
        having_group = re.search(having_pattern, q_str).group(1).strip()
        if having_group:
            if 'Search' in self.q_dict.keys():
                raise ValueError('Search values are already parsed')
            self._parse_having(having_group)
        else:
            raise ValueError('Search values in having part were not specified')

        return self.q_dict

    def _parse_find(self, find_part):
        """
        Parses find string part into list of specific keys to whih search values would be apllied
        e.g. 'sec(name, type) prop(name)' into {'Sec': ['name', 'type'], 'Prop': ['name']} .
        
        :param find_part: string which represent list of searchable odML data model objects 
                            like document(doc), sections(sec) or properties(prop).
                            e.g. 'sec(name, type) prop(name)'
        """
        doc_pattern = re.compile("(doc|document)\(.*?\)")
        doc = re.search(doc_pattern, find_part)
        if doc:
            self._parse_doc(doc)

        sec_pattern = re.compile("(sec|section)\(.*?\)")
        sec = re.search(sec_pattern, find_part)
        if sec:
            self._parse_sec(sec)

        prop_pattern = re.compile("(prop|property)\(.*?\)")
        prop = re.search(prop_pattern, find_part)
        if prop:
            self._parse_prop(prop)

    def _parse_doc(self, doc):
        p = re.compile("[\(|, ](id|author|date|version|repository|sections)[\)|,]")
        if doc:
            self.q_dict['Doc'] = re.findall(p, doc.group(0))

    def _parse_sec(self, sec):
        p = re.compile("[\(|, ](id|name|definition|type|repository|reference|sections|properties)[\)|,]")
        if sec:
            self.q_dict['Sec'] = re.findall(p, sec.group(0))

    def _parse_prop(self, prop):
        p = re.compile("[\(|, ](id|name|definition|dtype|unit|uncertainty|reference|value_origin)[\)|,]")
        if prop:
            self.q_dict['Prop'] = re.findall(p, prop.group(0))

    def _parse_having(self, having_part):
        """
        Parses search value string into list of specific values 
        e.g. 'Stimulus, Contrast, Date' into list [Stimulus, Contrast, Date].
        
        :param having_part: string with search values, e.g. 'Stimulus, Contrast'
                      Also spaces errors in the string like 'Stimulus,    ,  Contrast' will be ignored.
        """
        search_values_list = []
        search_params = re.compile("(.*?)(?:,|$)")
        if having_part:
            search_values = re.findall(search_params, having_part)
            for v in search_values:
                if v.strip():
                    search_values_list.append(v.strip())
        self.q_dict['Search'] = search_values_list


class QueryParser(BaseQueryParser):

    def __init__(self):
        super(QueryParser, self).__init__()

    def parse_query_string(self, q_str):
        """
        :param q_str: query string
                      Example: doc(author:D. N. Adams) section(name:Stimulus) prop(name:Contrast, value:20, unit:%)
        :return: dict object
                 Example: {'Sec': [('name', 'Stimulus')],
                           'Doc': [('author', 'D. N. Adams')],
                           'Prop': [('name', 'Contrast'), ('value':[20]), ('unit':'%')]}
        """
        doc_pattern = re.compile("(doc|document)\(.*?\)")
        doc = re.search(doc_pattern, q_str)
        if doc:
            self._parse_doc(doc)

        sec_pattern = re.compile("(sec|section)\(.*?\)")
        sec = re.search(sec_pattern, q_str)
        if sec:
            self._parse_sec(sec)

        prop_pattern = re.compile("(prop|property)\(.*?\)")
        prop = re.search(prop_pattern, q_str)
        if prop:
            self._parse_prop(prop)
        
        return self.q_dict

    def _parse_doc(self, doc):
        p = re.compile("[, |\(](id|author|date|version|repository|sections):(.*?)[,|\)]")
        if doc:
            self.q_dict['Doc'] = re.findall(p, doc.group(0))

    def _parse_sec(self, sec):
        p = re.compile("[, |\(](id|name|definition|type|repository|reference|sections|properties):(.*?)[,|\)]")
        if sec:
            self.q_dict['Sec'] = re.findall(p, sec.group(0))

    def _parse_prop(self, prop):
        p = re.compile("[, |\(](id|name|definition|dtype|unit|uncertainty|reference|value_origin):(.*?)[,|\)]")
        if prop:
            self.q_dict['Prop'] = re.findall(p, prop.group(0))

            p_value = re.compile("value:\[(.*)]")

            value_group = re.findall(p_value, prop.group(0))
            if value_group:
                values = re.split(", ?", value_group[0])
                self.q_dict['Prop'].append(('value', values))


class QueryCreator(BaseQueryCreator):
    """ 
    Class for simplifying the creation of prepared SPARQL queries 
    
    Usage:
        q = "doc(author:D. N. Adams) section(name:Stimulus) prop(name:Contrast, value:20, unit:%)"
        prepared_query = QueryCreator().get_query(q, QueryParser())
        
        q = "FIND sec(name, type) prop(name) HAVING Recording, Recording-2012-04-04-ab, Date"
        prepared_query = QueryCreator().get_query(q, QueryParser2())
    """

    def __init__(self, q_dict=None):
        """
        :param q_dict: dictionary with query parameters
        """
        super(QueryCreator, self).__init__(q_dict)

    def get_query(self, q_str=None, q_parser=None):
        """
        :param q_parser: one of possible query parsers.
        :param q_str: doc(author:D. N. Adams) section(name:Stimulus) prop(name:Contrast, value:20, unit:%)
        :return rdflib prepare query.
        """
        # TODO find out if the validation for the q_str is important
        # We can possibly warn about not used parts and print the parsed dictionary
        if not self.q_dict:
            if not q_str:
                raise AttributeError("Please fulfill q_str param (query string)")
            elif not q_parser:
                raise AttributeError("Please fulfill q_parser param (query parser)")
            self.q_dict = q_parser.parse_query_string(q_str)
        self._prepare_query()
        return prepareQuery(self.query, initNs={"odml": Namespace("https://g-node.org/projects/odml-rdf#"),
                                                "rdf": RDF})

    def _prepare_query(self):
        """
        Creates rdflib query using parameters from self.q_dict.
        :return: string representing rdflib query.
        """

        odml_uri = "https://g-node.org/projects/odml-rdf#"
        self.query = 'SELECT * WHERE {\n'

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
                            self.query += '?d {0} \"{1}\" .\n'.format(re.sub(odml_uri,
                                                                             "odml:", attr), i[1])
        if 'Sec' in self.q_dict.keys():
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
                            self.query += '?s {0} \"{1}\" .\n'.format(re.sub(odml_uri,
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
                            self.query += '?p {0} \"{1}\" .\n'.format(re.sub(odml_uri,
                                                                             "odml:", attr), i[1])

        self.query += '}\n'
        return self.query
