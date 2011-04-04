"""
Handles loading of terminology data for odML documents
"""
import urllib
import tools.xmlparser
import format

def load(obj, url):
    """
    imports a terminology into a section or document

    currently just loads the terminology and fills the section with it
    """

    fp = urllib.urlopen(url)
    doc = tools.xmlparser.parseXML(fp)

    assert len(doc.sections) > 0
    _store_self_mapping(doc)
    map_sections(doc, obj)

def _store_self_mapping(term):
    """
    install the _terminology_mapping field for all elements in *term*

    this is needed, because it gets copied by either clone() or map_attributes()
    """
    try:
        iterator = iter(term)
    except TypeError:
        return
    
    for obj in iterator:
        obj._terminology_mapping = obj
        _store_self_mapping(obj)

def map_attributes(term, obj, fmt):
    """
    maps class attributes from a terminology template *term* to an odml object *obj*
    using format information of format-class instance *fmt*
    """
    obj._terminology_mapping = term._terminology_mapping

    for key in fmt:
        if not hasattr(obj, key) or getattr(obj, key) is None:
            setattr(obj, key, getattr(term, key))

def map_sections(term, obj):
    """
    maps each section of a terminology document *term* to a corresponding section
    in the odml *obj* or creates one
    """
    # recursively map subsections
    for sec in term.sections:
        try:
            map_section(sec, obj.sections[sec.name])
        except KeyError:
            obj.append(sec.clone())

def map_section(term, section):
    """
    maps a terminology section *term* to an odml document section *section*
    """

    # map all section attributes
    map_attributes(term, section, format.Section)
    map_sections(term, section)

    # map all properties
    for prop in term.properties:
        try:
            map_property(prop, section.properties[prop.name])
        except KeyError:
            section.append(prop.clone())

def map_property(term, prop):
    """
    maps a terminology property *term* to an odml document property *prop*
    """

    # map all property attributes
    map_attributes(term, prop, format.Property)

    # now map values if applicable
    if len(term.values) == len(prop.values):
        for i in xrange(0, len(term.values)):
            map_attributes(term.values[i], prop.values[i], format.Value)
