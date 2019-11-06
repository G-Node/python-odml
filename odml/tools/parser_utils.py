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
    pass


class InvalidVersionException(ParserException):
    """
    Exception wrapper to indicate a non-compatible odML version.
    """
    pass
