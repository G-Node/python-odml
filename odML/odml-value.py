
class Value(object):
    """A odML value"""
    def __init__(self, value, dtype=None):
        self._value = value
        self._dtype = None

    @property
    def data(self):
        return self._value

    @data.setter
    def data (self, new_value):
        self._data = new_value

    @property
    def dtype(self):
        return self._dtype
    
    @dtype.setter
    def dtype(self, new_type):
        self._dtype = new_type
        
    @property
    def uncertainty(self):
        return self._uncertainty

    @uncertainty.setter
    def uncertainty(self, new_value)
        self._uncertainty = new_value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, new_value):
        self._unit = new_value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_value):
        self._id = new_value

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, new_value):
        self.comment = new_value    

    @property
    def default_filename(self):
        return self._default_filename

    @default_filename.setter
    def default_filename(self, new_value):
        self._default_filename = new_value
