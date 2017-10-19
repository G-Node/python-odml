import os
from .tools.odmlparser import ODMLReader, ODMLWriter

parsers = ["xml", "json", "yaml"]


def load(filename, backend="xml"):
    if not os.path.exists(filename):
        raise FileNotFoundError("File \'%s\' was not found!" % (filename if len(filename) < 20 else "...%s" % filename[19:]))
    reader = ODMLReader(backend)
    return reader.from_file(filename)


def save(obj, filename, backend="xml"):
    writer = ODMLWriter(backend)
    if "." not in filename.split(os.pathsep)[-1]:
        filename = filename + ".%s" % backend
    return writer.write_file(obj, filename)


def display(obj, backend="xml"):
    writer = ODMLWriter(backend)
    print(writer.to_string(obj))
