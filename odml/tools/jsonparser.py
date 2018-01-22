#!/usr/bin/env python
"""
The JSON import/export module.
This is rudimentary for now, assuming everything is well-formed.
"""
import sys
import odml
import json

try:
    unicode = unicode
except NameError:
    unicode = str


class OdmlSerializer(object):
    """
    Converts the odml class hierarchy to dictionaries and lists
    """

    def __init__(self, odml_document):
        self.doc = odml_document

    @staticmethod
    def save_element(e):
        """
        Returns an xml node for the odML object e
        """
        fmt = e._format
        cur = {'_type': fmt.__class__.__name__}

        # Generate elements
        for k in fmt._args:
            if not hasattr(e, fmt.map(k)):
                continue

            val = getattr(e, fmt.map(k))
            if val is None:
                continue

            if isinstance(val, list):
                for v in val:
                    ele = OdmlSerializer.save_element(v)
                    cur.setdefault(k, []).append(ele)
            else:
                if sys.version_info < (3, 0):
                    cur[k] = unicode(val)
                else:
                    cur[k] = str(val)

        return cur


JSON_VERSION = "1"


class JSONWriter(OdmlSerializer):

    def __unicode__(self):
        doc = self.save_element(self.doc)
        doc['_version'] = JSON_VERSION
        return json.dumps(doc)

    def __str__(self):
        doc = self.save_element(self.doc)
        doc['_version'] = JSON_VERSION
        return json.dumps(doc)

    def write_file(self, filename):
        if sys.version_info < (3, 0):
            data = unicode(self)
        else:
            data = str(self)
        f = open(filename, "w")
        f.write(data)
        f.close()


class OdmlReader(object):
    """
    Opposite of OdmlSerializer: converts dictionaries representing
    odml objects back to their classes
    """

    def to_odml(self, obj):
        fmt = getattr(odml.format, obj['_type'])
        kargs = {}
        objects = []
        for k in fmt._args:
            v = obj.get(k, None)
            if isinstance(v, list):
                for i, nobj in enumerate(v):
                    objects.append(self.to_odml(nobj))
            elif v is not None:
                kargs[fmt.map(k)] = v
        return getattr(self, "create_%s" % fmt.name())(fmt, kargs, obj, objects)

    def create_odML(self, fmt, kargs, obj, children):
        obj = fmt.create(**kargs)
        for i in children:
            obj.append(i)
        return obj

    create_section = create_odML
    create_value = create_odML

    def create_property(self, fmt, kargs, obj, children):
        kargs['value'] = children
        return self.create_odML(fmt, kargs, obj, [])


class JSONReader(OdmlReader):

    def fromString(self, data):
        obj = json.loads(data)
        return self.to_odml(obj)

    def fromFile(self, infile):
        return self.fromString(infile.read())


if __name__ == "__main__":
    # import sys
    y = JSONReader().fromFile(sys.stdin)
    import dumper
    dumper.dumpDoc(y)
