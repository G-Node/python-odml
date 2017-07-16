from rdflib import Namespace

import odml

"""
A module providing general format information
and mappings of xml-attributes to their python class equivalents
"""

class Format(object):
    _map = {}
    _rev_map = None
    _rdf_map = {}
    _rdf_type = None
    _ns = Namespace("https://g-node.org/projects/odml-rdf#")

    def map(self, name):
        """ Maps an odml name to a python name """
        return self._map.get(name, name)

    def rdf_map(self, name):
        """ Maps a python name to a odml rdf namespace """
        return self._rdf_map.get(name, name)

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
            for k, v in self._map.iteritems():
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
    }
    _map = {
        'dependencyvalue': 'dependency_value',
        'type': 'dtype'
    }
    _rdf_map = {
        'id': _ns.id,
        'name': _ns.name,
        'definition': _ns.definition,
        'dtype': _ns.dtype,
        'unit': _ns.unit,
        'uncertainty': _ns.uncertainty,
        'value': _ns.hasValue
    }


class Section(Format):
    _name = "section"
    _ns = Format._ns
    _rdf_type = _ns.Section
    _args = {
        'id': 0,
        'type': 1,
        'name': 0,
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
    }
    _rdf_map = {
        'id': _ns.id,
        'name': _ns.name,
        'definition': _ns.definition,
        'type': _ns.type,
        'repository': _ns.terminology,
        'reference': _ns.reference,
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
        'section': 'sections'
    }
    _rdf_map = {
        'id': _ns.id,
        'author': _ns.author,
        'date': _ns.date,
        # 'doc_version': _ns.docversion,    # discuss about the changes to the data model
        'repository': _ns.terminology,
        'sections': _ns.hasSection,
        'version': _ns['doc-version'],
    }


Document = Document()
Section = Section()
Property = Property()

__all__ = [Document, Section, Property]
