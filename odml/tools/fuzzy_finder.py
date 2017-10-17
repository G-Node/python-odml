from odml.tools.query_creator import QueryCreator, QueryParser, QueryParserFuzzy


class FuzzyFinder(object):
    """
    FuzzyFinder tool for querying graph through 'fuzzy' queries. 
    If the user do not know exact attributes and structure of the odML data model,
    the finder executes multiple queries to better match the parameters and returns sets of triples.
    """
    def __init__(self, graph=None, q_params=None):
        self.graph = graph
        self.q_params = q_params
        self.prepared_queries_list = []
        self._subsets = []

    def find(self, mode='fuzzy', graph=None, q_str=None, q_params=None):
        # TODO warn users if they added non-odml attributes ('naming' instead of 'name' e.g.)
        """
        Apply set of queries to the graph and returns info that was retrieved from queries.
        
        :param mode:     define the type of parser which will be used for parsing parameters or queries.
                         Please find our more info about concrete parsers in odml/tool/query_creator.py or tutorials.
        :param graph:    graph object.
        :param q_str:    query string which used in QueryCreator class.
                         Example for QueryParser: doc(author:D. N. Adams) section(name:Stimulus) prop(name:Contrast, value:20, unit:%)
                         Example for QueryParserFuzzy: "FIND sec(name) prop(type) HAVING Stimulus, Contrast"
        :param q_params: dictionary object with set of parameters for a query
                         Example for QueryParser: {'Sec': [('name', 'Stimulus')],
                                                   'Doc': [('author', 'D. N. Adams')],
                                                   'Prop': [('name', 'Contrast'), ('value':[20, 25]), ('unit':'%')]}
                         Example for QueryParserFuzzy: {'Sec': ['name', 'type'],
                                                        'Doc': ['author'],
                                                        'Search': ['Stimulus', 'Contrast']}
        :return:         string which contains set of triples.
        """
        if mode == 'fuzzy':
            q_parser = QueryParserFuzzy()
            pairs_generator = self._generate_parameters_pairs_fuzzy
        elif mode == 'match':
            q_parser = QueryParser()
            pairs_generator = self._generate_parameters_pairs
        else:
            raise ValueError("Parameter mode can be either 'fuzzy' or 'match'")

        self._validate_find_input_attributes(graph, q_str, q_params, q_parser)

        self._generate_parameters_subsets(pairs_generator())

        return self._output_query_results()

    def _validate_find_input_attributes(self, graph, q_str, q_params, q_parser):
        if not graph and not self.graph:
            raise ValueError("Please provide a RDF graph")

        if not self.graph:
            self.graph = graph

        if q_str and q_params:
            raise ValueError("Please pass query parameters only as a string or a dict object")

        if q_str:
            self.q_params = q_parser.parse_query_string(q_str)
        elif q_params:
            self.q_params = q_params
        else:
            raise ValueError("Please pass query parameters either as a string or a dict object")

    def _generate_parameters_pairs(self):
        """
        Example: {'Sec': [('name', 'some_name'), ('type', 'Stimulus')]}
        :return: [('Sec', ('name', 'some_name')), ('Sec', ('type', 'Stimulus'))]
        """
        parameters_pairs = []
        possible_keys = QueryCreator.possible_q_dict_keys
        for key in possible_keys:
            if key in self.q_params.keys():
                object_attrs = self.q_params[key]
                for object_attr in object_attrs:
                    s = tuple([key, object_attr])
                    parameters_pairs.append(s)
        return parameters_pairs

    def _generate_parameters_pairs_fuzzy(self):
        """
        Generates set of tuples matching search select and where parts of fuzzy finder query
        from dictionary of parameters.
        
        Example:  {'Sec': ['name', 'type'],
                   'Doc': ['author'],
                   'Search': ['Stimulus', 'Contrast']} 
        :return:  [('Sec', ('name', 'Stimulus')), ('Sec', ('name', 'Contrast')), 
                   ('Sec', ('type', 'Stimulus')), ('Sec', ('name', 'Contrast')),
                   ('Doc', ('author', 'Stimulus')), ('Doc', ('author', 'Contrast'))]
        """
        parameters_pairs = []
        search_values = []
        possible_keys = QueryCreator.possible_q_dict_keys
        if 'Search' in self.q_params.keys():
            search_values = self.q_params['Search']

        for key in possible_keys:
            if key in self.q_params.keys():
                object_attrs = self.q_params[key]
                for object_attr in object_attrs:
                    for value in search_values:
                        parameters_pairs.append(tuple([key, tuple([object_attr, value])]))
        return parameters_pairs

    def _generate_parameters_subsets(self, attrs):
        """
        Generates the set of parameters to create queries from specific to more broad ones.
        """
        self._subsets = []
        if len(attrs) > 0:
            self._subsets_util_dfs(0, [], self._subsets, sorted(attrs))

        self._subsets.sort(key=len, reverse=True)

    def _subsets_util_dfs(self, index, path, res, attrs):
        """
        Generates all subsets of attrs set using Depth-first search.
        Example (with numbers for explicity: [1,2,3] -> [[1], [2], [3], [1,2], [1,3], [2,3], [1,2,3]]
        
        :param index: help index for going through list.
        :param path:  array for saving subsets.
        :param res:   result subset.
        :param attrs: input list of attrs e.g. [('Sec', ('name', 'some_name')), ('Sec', ('type', 'Stimulus'))]
        """
        if path:
            res.append(path)
        for i in range(index, len(attrs)):
            if self._check_duplicate_attrs(path, attrs[i]):
                self._subsets_util_dfs(i + 1, path + [attrs[i]], res, attrs)

    @staticmethod
    def _check_duplicate_attrs(attrs_list, attr):
        for i in attrs_list:
            if attr[1][0] == i[1][0]:
                return False
        return True

    def _output_query_results(self):
        output_triples_string = ""
        # TODO define when we want to stop loop, influence factors(time, previous result etc.)
        for query in self._subsets:
            # FIXME we do need really need to have QueryCreator object
            # put it here to write initial query to output string for explicity
            creator = self._prepare_query(query)
            q = creator.get_query()

            triples = self._execute_query(q)
            if triples:
                output_triples_string += creator.query
                output_triples_string += triples
                output_triples_string += '\n'

        return output_triples_string

    def _execute_query(self, query):
        """
        Execute prepared query on the graph.
        
        :param query: prepared query object
        :return: string with output triples
        """
        output_string = ""
        for row in self.graph.query(query):
            row_string = self._build_output_str(row)
            output_string += row_string
        return output_string

    @staticmethod
    def _build_output_str(row):
        """
        Build output string depending on the query variables.
        
        :param row: rdflib query row.
        :return: string with values.
        """
        out_str = ""
        possible_vars = QueryCreator.possible_query_variables

        for v in possible_vars.keys():
            try:
                val = getattr(row, v)
                out_str += '{0}: {1}\n'.format(possible_vars[v], val)
            except AttributeError:
                pass
        return out_str

    @staticmethod
    def _prepare_query(args):
        """
        Return a query for given parameters.
        
        :param args: dict with list of odML object attributes for creation query
                     Example: {'Sec': [('name', 'some_name'), ('type', 'Stimulus')]}
        :return: QueryCreator object.
        """
        q_params = {}
        for arg in args:
            if arg[0] in q_params:
                q_params[arg[0]].append(arg[1])
            else:
                q_params[arg[0]] = [arg[1]]
        creator = QueryCreator(q_params)
        return creator
