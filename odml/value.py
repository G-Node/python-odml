class Value(object):
    """
    An odML value
    
    value
        mandatory, its the value = content itself.
    
    uncertainty (optional)
        an estimation of the value's uncertainty.
    
    unit (optional)
        the value's unit
    
    dtype (optional)
        the data type of the value

    id (optional)
        an external reference number (e.g. entry in a database)
    
    defaultFileName (optional)
        the default file name which should be used when saving the object
    
    definition
        optional, here additional comments on the value of the property can be given
        
    TODO: comment
    """
    def __init__(self, value, uncertainty=None, unit=None, dtype=None, definition=None, id=None, defaultFileName=None, comment=None):
        self._value  = value
        self._dtype  = None
        self._property = None
        #TODO fix other values
        #TODO validate arguments
        
        self._unit = unit
        self._uncertainty = uncertainty
        self._dtype = dtype
        self._definition = definition
        self._id = id
        self._defaultFileName = defaultFileName
        self._comment = comment

    def __repr__(self):
        if self._dtype:
            return "<%s %s>" % (str(self._dtype), str(self._value))
        return "<%s>" % str(self._value)

    @property
    def data(self):
        return self._value

    @data.setter
    def data (self, new_value):
        self._value = new_value
        
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

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
    def uncertainty(self, new_value):
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
    def definition(self):
        return self._definition

    @definition.setter
    def definition(self, new_value):
        self._definition = new_value

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, new_value):
        self._comment = new_value    

    @property
    def default_filename(self):
        return self._default_filename

    @default_filename.setter
    def default_filename(self, new_value):
        self._default_filename = new_value
