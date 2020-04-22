"""
Utility file to provide constants, exceptions and functions
commonly used by the odML tools parsers and converters.
"""

SUPPORTED_PARSERS = ['XML', 'YAML', 'JSON', 'RDF']


RDF_CONVERSION_FORMATS = {
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


class ParserException(Exception):
    """
    Exception wrapper used by various odML parsers.
    """


class InvalidVersionException(ParserException):
    """
    Exception wrapper to indicate a non-compatible odML version.
    """


def odml_tuple_export(odml_tuples):
    """
    Converts odml style tuples to a parsable string representation.
    Every tuple is represented by brackets '()'. The individual elements of a tuple are
    separated by a semicolon ';'. The individual tuples are separated by a comma ','.
    An odml 3-tuple list of 2 tuples would be serialized to: "[(11;12;13),(21;22;23)]".

    :param odml_tuples: List of odml style tuples.
    :return: string
    """
    str_tuples = ""
    for val in odml_tuples:
        str_val = ";".join(val)
        if str_tuples:
            str_tuples = "%s,(%s)" % (str_tuples, str_val)
        else:
            str_tuples = "(%s)" % str_val

    return "[%s]" % str_tuples
