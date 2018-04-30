"""
Utility file to provide constants, exceptions and functions
commonly used by the odML tools parsers and converters.
"""

SUPPORTED_PARSERS = ['XML', 'YAML', 'JSON', 'RDF']


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
