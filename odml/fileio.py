from .tools.odmlparser import ODMLReader, ODMLWriter

parsers = ["xml", "json", "yaml"]


def load(filename, backend="xml"):
    reader = ODMLReader(backend)
    return reader.from_file(filename)


def save(obj, filename, backend="xml"):
    writer = ODMLWriter(backend)
    return writer.write_file(obj, filename)


def display(obj, backend="xml"):
    writer = ODMLWriter(backend)
    print(writer.to_string(obj))
