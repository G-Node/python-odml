
import Event

class Section(object):
    """A odML Section"""
    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent

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


    
