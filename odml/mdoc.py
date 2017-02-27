# -*- coding: utf-8 -*-
import odml

# Extent odml.doc.BaseDocument
class mdoc(odml.doc.BaseDocument):
    def __init__(self,  author=None, date=None, version=None, repository=None):
        odml.doc.BaseDocument.__init__(self, author, date, version, repository) 

    def mappend(self, *obj_tuple):
        ll = len(obj_tuple)
        for i in range(0,ll):
            self.append(obj_tuple[i])

