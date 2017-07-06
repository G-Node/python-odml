import odml
from rdflib import Namespace

"""
A module providing general format information
and mappings of rdf-attributes to their python class equivalents
"""


class RDFFormat(object):

    _map = {}
    _rev_map = None
    _ns = Namespace("http://g-node/odml#")

    def map(self, name):
        """ Maps a python name to a odml rdf namespace """
        return self._map.get(name, name)

    def revmap(self, name):
        """ Maps a odml rdf namespace to a python name """
        if self._rev_map is None:
            # create the reverse map only if requested
            self._rev_map = {}
            for k, v in self._map.items():
                self._rev_map[v] = k
        return self._rev_map.get(name, name)

    def __iter__(self):
        """ Iterates each python property name """
        for k in self._map:
            yield self.map(k)

    def create(self, *args, **kargs):
        return getattr(odml, self.__class__.__name__)(*args, **kargs)


class Property(RDFFormat):
    _ns = super()._ns
    _map = {
        'id': _ns.id,
        'name': _ns.name,
        'definition': _ns.definition,
        'dtype': _ns.dtype,
        'unit': _ns.unit,
        'uncertainty': _ns.uncertainty,
        'values': _ns.hasValue  # manage datatype RDF:Bag, RDF:li
    }


class Section(RDFFormat):
    _ns = super()._ns
    _map = {
        'id': _ns.id,
        'name': _ns.name,
        'definition': _ns.definition,
        'type': _ns.type,
        'repository': _ns.terminology,
        'reference': _ns.reference,
        'sections': _ns.hasSection,
        'properties': _ns.hasProperty,

        # TODO find out the way to correctly represent link & include
        # 'link'
        # 'include'
    }


class Document(RDFFormat):
    _ns = super()._ns
    _map = {
        'id': _ns.id,
        'author': _ns.author,
        'date': _ns.date,   # manage datatype
        'doc_version': _ns.docversion,
        'repository': _ns.terminology,
        'sections': _ns.hasSection,
        'version': _ns.version,
    }

Document = Document()
Section = Section()
Property = Property()

__all__ = [Document, Section, Property]
