# -*- coding: utf-8 -*-
import odml

# Extent odml.section.BaseSection       
class msec(odml.section.BaseSection):
    def __init__(self, name, type="undefined", parent=None, definition=None):
        odml.section.BaseSection.__init__(self, name, type, parent, definition) 

    def mappend(self, *obj_tuple):
        ll = len(obj_tuple)
        for i in range(0,ll):
            self.append(obj_tuple[i])
