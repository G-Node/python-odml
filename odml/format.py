import sys

from rdflib import Namespace

import odml

"""
A module providing general format information
and mappings of xml-attributes to their python class equivalents
"""


class Format(object):
    _name = ""
    _args = {}
    _map = {}
    _rev_map = None
    _rdf_map = {}
    _rdf_type = None
    _ns = Namespace("https://g-node.org/projects/odml-rdf#")

    @property
    def name(self):
        """Returns the name of the current odML format"""
        return self._name

    @property
    def arguments(self):
        """Returns all items in the current odML format argument dict"""
        return self._args.items()

    @property
    def arguments_keys(self):
        """Returns all keys of the current odML format argument dict"""
        return self._args.keys()

    def map(self, name):
        """ Maps an odml name to a python name """
        return self._map.get(name, name)

    @property
    def map_keys(self):
        """Returns all keys of the current odML format map dict"""
        return self._map.keys()

    def rdf_map(self, name):
        """ Maps a python name to a odml rdf namespace """
        return self._rdf_map.get(name, name)

    @property
    def rdf_map_keys(self):
        """Returns all keys of the current odML format RDF map dict"""
        return self._rdf_map.keys()

    @property
    def rdf_map_items(self):
        """Returns all items of the current odML format RDF map dict"""
        return self._rdf_map.items()

    @property
    def rdf_type(self):
        """ Return rdf type of an object """
        return self._rdf_type

    @staticmethod
    def namespace():
        """ Return current link to current odml namespace"""
        return Format._ns

    def revmap(self, name):
        """ Maps a python name to an odml name """
        if self._rev_map is None:
            # create the reverse map only if requested
            self._rev_map = {}
            if sys.version_info < (3, 0):
                for k, v in self._map.iteritems():
                    self._rev_map[v] = k
            else:
                for k, v in self._map.items():
                    self._rev_map[v] = k
        return self._rev_map.get(name, name)

    def __iter__(self):
        """ Iterates each python property name """
        for k in self._args:
            yield self.map(k)

    def create(self, *args, **kargs):
        return getattr(odml, self.__class__.__name__)(*args, **kargs)


class Property(Format):
    _name = "property"
    _ns = Format._ns
    _rdf_type = _ns.Property
    _args = {
        'id': 0,
        'name': 1,
        'value': 0,
        'unit': 0,
        'definition': 0,
        'dependency': 0,
        'dependencyvalue': 0,
        'uncertainty': 0,
        'reference': 0,
        'type': 0,
        'value_origin': 0
    }
    _map = {
        'dependencyvalue': 'dependency_value',
        'type': 'dtype',
        'id': 'oid'
    }
    _rdf_map = {
        'id': _ns.hasId,
        'name': _ns.hasName,
        'definition': _ns.hasDefinition,
        'dtype': _ns.hasDtype,
        'unit': _ns.hasUnit,
        'uncertainty': _ns.hasUncertainty,
        'reference': _ns.hasReference,
        'value': _ns.hasValue,
        'value_origin': _ns.hasValueOrigin
    }


class Section(Format):
    _name = "section"
    _ns = Format._ns
    _rdf_type = _ns.Section
    _args = {
        'id': 0,
        'type': 1,
        'name': 1,
        'definition': 0,
        'reference': 0,
        'link': 0,
        'repository': 0,
        'section': 0,
        'include': 0,
        'property': 0
    }
    _map = {
        'section': 'sections',
        'property': 'properties',
        'id': 'oid'
    }
    _rdf_map = {
        'id': _ns.hasId,
        'name': _ns.hasName,
        'definition': _ns.hasDefinition,
        'type': _ns.hasType,
        'repository': _ns.hasTerminology,
        'reference': _ns.hasReference,
        'sections': _ns.hasSection,
        'properties': _ns.hasProperty,
    }


class Document(Format):
    _name = "odML"
    _ns = Format._ns
    _rdf_type = _ns.Document
    _args = {
        'id': 0,
        'version': 0,
        'author': 0,
        'date': 0,
        'section': 0,
        'repository': 0,
    }
    _map = {
        'section': 'sections',
        'id': 'oid'
    }
    _rdf_map = {
        'id': _ns.hasId,
        'author': _ns.hasAuthor,
        'date': _ns.hasDate,
        'version': _ns.hasDocVersion,    # discuss about the changes to the data model
        'repository': _ns.hasTerminology,
        'sections': _ns.hasSection
    }


Document = Document()
Section = Section()
Property = Property()

__all__ = [Document, Section, Property]
