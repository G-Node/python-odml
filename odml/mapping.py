import terminology

class mapable(object):
    """
    Provides assisting functionality for objects that support
    the mapping attribute (i.e. sections and properties)
    """
    def get_mapping(self):
        """
        returns the current valid mapping for this section / property
        which may be defined by the object itsself, by its terminology equivalent
        or inherited from its parent
        """
        mapping = self.mapping
        if mapping is None:
            if self.parent.parent is not None: # i.e. not the root node
                return self.parent.get_mapping()
        return (self, mapping)

    @staticmethod
    def parse_mapping(url):
        """
        parse u url of format http://host/file.xml#section_type:property_name

        returns a 3-tuple: (url, stype, prop_name)
        where stype or prop_name may be None
        """
        stype = None
        prop_name = None
        if '#' in url:
            url, stype = url.split('#', 1)
            if ':' in stype:
                stype, prop_name = stype.split(':', 1)
        terminology.deferred_load(url)
        return (url, stype, prop_name)

    @staticmethod
    def get_mapping_object(url):
        """
        returns the object instance a mapping-url points to
        """
        url, stype, prop_name = mapable.parse_mapping(url)
        term = terminology.load(url)
        if stype is None:
            return term.sections[0]
        sec = term.find_related(type=stype)
        if sec is None:
            return None
        if prop_name is None:
            return sec
        return sec.properties[prop_name]

    @property
    def mapped_object(self):
        """
        if there is a mapping defined (or inherited), returns the corresponding
        mapping object
        """
        url = self.mapping
        if url is not None:
            return self.get_mapping_object(url)

        return None
        #if self.parent is not None: # i.e. not the root node
        #    obj = self.parent.mapped_object
        #    if obj is not None:
        #        return obj.contains(self)

    @property
    def mapping(self):
        if self._mapping is None:
            term = self.get_terminology_equivalent()
            if term is not None:
                return term._mapping
        return self._mapping

    @mapping.setter
    def mapping(self, new_value):
        term = self.get_terminology_equivalent()
        if term is not None and term._mapping == new_value:
            new_value = None
        self._mapping = new_value

class MappingError(TypeError):
    pass

def apply_mapping(doc):
    # iterate each section and property
    # take the mapped object and try to put it at a meaningful place
    for sec in doc.itersections(recursive=True):
        obj = sec.mapped_object
        if obj is None: continue

        sec.type = obj.type
        sec.mapping = None
        term = obj.get_repository()
        if sec.get_repository() != term:
            sec.repository = obj.get_repository()

    for sec in doc.itersections(recursive=True):
        for prop in sec.properties:
            mapping = prop.mapped_object
            if mapping is None: continue

            dst_type = mapping._section.type
            # rule 4c: target-type == section-type
            #          copy attributes, keep property
            if dst_type == sec.type:
                prop.name = mapping.name
                prop.mapping = None
                continue

            # rule 4d: one child has the type
            child = sec.find_related(type=dst_type, siblings=False, parents=False, findAll=True)
            if child is None:
                # rule 4e: a sibling has the type
                sibling = sec.find_related(type=dst_type, children=False, parents=False)
                if sibling is not None:
                    rel = sibling.find_related(type=sec.type, findAll=True)
                    if len(rel) > 1:
                        # rule 4e2: create a subsection linked to the sibling
                        child =  mapping._section.clone(children=False)
                        sec.remove(prop)
                        prop.name = mapping.name
                        child.append(prop)
                        sec.append(child)
                        child._link = sibling.get_path()
                        continue

                    # rule 4e1: exactly one relation for sibling
                child = sibling # once we found the target section, the code stays the same
            elif len(child) > 1:
                raise MappingError("""Your data organisation does not make sense,
                there are %d children of type '%s'. Don't know how to handle.""" % (len(child), dst_type))
            else: # exactly one child found
                child = child[0]

            if child is None:
                # rule 4f: need to add a section
                child = mapping._section.clone(children=False)
                sec.parent.append(child)

            if child is not None:
                sec.remove(prop)
                child.append(prop)
                prop.name = mapping.name
                prop.mapping = None
                continue


def map_property(doc, prop):
    obj = prop.mapped_obj
    if obj is None: return False
    insert_to_tree(doc, obj, prop)
    return True

def section_template(sec):
    import copy
    obj = copy.copy(sec)
    sec._sections = base.SmartList()
    sec._props = base.SmartList()
    return sec

def insert_to_tree(doc, obj, val):
    parents = []
    cur = obj
    while cur.parent is not None:
        cur = cur.parent
        parents.insert(0, cur)

    cur = doc
    for node in parents:
        dst = cur.contains(parents[0])
        if dst is None:
            dst = section_template(parents[0])
            cur.append(dst)
            #dst.include = parents[0].document.url + "#" + parents[0].type
        cur = dst

    val = val.clone()
    val.name = obj.name
