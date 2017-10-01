import pprint
import time

from odml.tools.query_creator import QueryCreator


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

    def find(self, graph, q_str=None, q_params=None):
        """
        Apply set of queries to the graph and returns info that was retrieved from queries.
        
        :param graph: graph object
        :param q_params: dictionary object with set of parameters for a query
        :param q_str: query string which used in QueryCreator class
        :return: string which contains set of triples
        """
        self.graph = graph
        if q_str and q_params:
            raise ValueError("Please pass query parameters either as string or dict object")

        if q_str:
            creator = QueryCreator()
            creator.parse_query_string(q_str)
            self.q_params = creator.q_dict
        elif q_params:
            self.q_params = q_params

        self._generate_parameters_subsets()

        output_triples_string = ""
        # TODO define when we want to stop loop, influence factors(time, previous result etc.)
        for query in self._subsets:
            q = self._prepare_query(query)
            triples = self._execute_query(q)
            if triples:
                output_triples_string += q
                output_triples_string += triples
        return output_triples_string

    def _subsets_util_dfs(self, index, path, res, attrs):
        """
        Generates all subsets of attrs set using Depth-first search
        Example (with numbers for explicity: [1,2,3] -> [[], [1], [2], [3], [1,2], [1,3], [2,3], [1,2,3]]
        :param index: help index for going through list
        :param path: array for saving subsets
        :param res: result subset
        :param attrs: input list of attrs e.g. [('Sec', ('name', 'some_name')), ('Sec', ('type', 'Stimulus'))]
        """
        if path:
            res.append(path)
        for i in range(index, len(attrs)):
            self._subsets_util_dfs(i + 1, path + [attrs[i]], res, attrs)

    def _generate_parameters_subsets(self):
        """
        Generates the set of parameters to create queries from specific to more broad ones.
        """
        attrs = []
        possible_keys = QueryCreator.possible_q_dict_keys
        for key in possible_keys:
            if key in self.q_params.keys():
                sec_attrs = self.q_params[key]
                for i in sec_attrs:
                    s = tuple([key, i])
                    attrs.append(s)

        if len(attrs) > 0:
            self._subsets_util_dfs(0, [], self._subsets, sorted(attrs))

        self._subsets.sort(key=len, reverse=True)
        pprint.pprint(self._subsets)  # debug statement, left to explicitly show the list of subsets

    def _execute_query(self, query):
        """
        Execute prepared query on the graph
        :param query: prepared query object
        :return: string with output triples
        """
        t0 = time.perf_counter()
        output_string = ""
        for row in self.graph.query(query):
            row_string = self._build_output_str(row)
            output_string += row_string
        t1 = time.perf_counter()
        print('Execution time: ', t1-t0)  # left for debug and benchmarking
        return output_string

    @staticmethod
    def _build_output_str(row):
        """
        Build output string depending on the query variables
        :param row: rdflib query row
        :return: string with values
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
        Return a query for given parameters
        :param args: dict with list of odML object attributes for creation query
                     Example: {'Sec': [('name', 'some_name'), ('type', 'Stimulus')]}
        :return: rdflib prepared query
        """
        q_params = {}
        for arg in args:
            if arg[0] in q_params:
                q_params[arg[0]].append(arg[1])
            else:
                q_params[arg[0]] = [arg[1]]
        creator = QueryCreator(q_params)
        return creator.prepare_query()
