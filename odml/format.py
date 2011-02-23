"""
A module providing general format information
and mappings of xml-attributes to their python class equivalents
"""
class Format(object):
    _rev_map = None
    def map(self, name):
        return self._map.get(name, name)
    def revmap(self, name):
        if self._rev_map is None:
            # create the reverse map only if requested
            self._rev_map = {}
            for k,v in self._map.iteritems():
                self._rev_map[v] = k
        return self._rev_map.get(name, name)

class Value(Format):
    _args = {
        'uncertainty': 0,
        'unit': 0,
        'type': 0,
        'definition': 0,
        'id': 0,
        'defaultFileName': 0
        }
    _map = {'type': 'dtype'}
    
class Property(Format):
    _args = {
        'name': 1,
        'value': 1,
        'synonym': 0,
        'definition': 0,
        'mapping': 0,
        'dependency': 0,
        'dependencyValue': 0
        }

class Section(Format):
    _args = {
        'type': 1,
        'name': 0,
        'definition': 0,
        'id': 0,
        'link': 0,
        'import': 0,
        'repository': 0,
        'mapping': 0,
        'section': 0,
        'property': 0
        }

Section  = Section()
Value    = Value()
Property = Property()

__all__ = [Section, Property, Value]
