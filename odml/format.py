import odml
"""
A module providing general format information
and mappings of xml-attributes to their python class equivalents
"""


class Format(object):
    _map = {}
    _rev_map = None

    def map(self, name):
        """maps an odml name to a python name"""
        return self._map.get(name, name)

    def revmap(self, name):
        """maps a python name to an odml name"""
        if self._rev_map is None:
            # create the reverse map only if requested
            self._rev_map = {}
            for k, v in self._map.iteritems():
                self._rev_map[v] = k
        return self._rev_map.get(name, name)

    def __iter__(self):
        """iterates each python property name"""
        for k in self._args:
            yield self.map(k)

    def create(self, *args, **kargs):
        return getattr(odml, self.__class__.__name__)(*args, **kargs)


class Value(Format):
    _name = "value"
    _args = {
        'value': 0,
        'uncertainty': 0,
        'unit': 0,
        'type': 0,
        'definition': 0,
        'reference': 0,
        }
    _map = {'type': 'dtype'}


class Property(Format):
    _name = "property"
    _args = {
        'name': 1,
        'value': 1,
        'definition': 0,
        'dependency': 0,
        'dependencyvalue': 0
        }
    _map = {
        'value': 'values',
        'dependencyvalue': 'dependency_value',
        'type': 'dtype'
        }


class Section(Format):
    _name = "section"
    _args = {
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


class Document(Format):
    _name = "odML"
    _args = {
        'version': 0,
        'author': 0,
        'date': 0,
        'section': 0,
        'repository': 0,
        }
    _map = {
        'section': 'sections'
        }

Document = Document()
Section = Section()
Value = Value()
Property = Property()

__all__ = [Document, Section, Property, Value]
