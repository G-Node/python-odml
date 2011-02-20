
class Property(object):
    """A odML Property"""
    def __init__(self, name, section=None):
        self._name = name
        self._section = section

    #odML "native" properties
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_value):
        self._name = new_value



    # API (public) 
    #
    #  properties
    @property
    def position(self):    
        return None #FIXME: IMPLEMENT

    @property
    def next(self):
        return None #FIXME: IMPLEMENT

    @property
    def values(self):
        return self._values

    # API (private)
    def _fire_change_event(self, prop_name):
        return None #FIXME: IMPLEMENT
