import os
from .tools.odmlparser import ODMLReader, ODMLWriter


def load(filename, backend="xml"):
    """
    Load an odML document from file.
    :param filename: Path and filename from where the odML document
                     is to be loaded and parsed.
    :param backend: File format of the file containing the odML document.
                    The default format is XML.
    :return: The parsed odML document.
    """
    if not os.path.exists(filename):
        msg = "File \'%s\' was not found!" % \
              (filename if len(filename) < 20 else "...%s" % filename[19:])
        raise FileNotFoundError(msg)

    reader = ODMLReader(backend)
    return reader.from_file(filename)


def save(obj, filename, backend="xml"):
    """
    Save an open odML document to file of a specified format.
    :param obj: odML document do be saved.
    :param filename: Filename and path where the odML document
                     should be saved.
    :param backend: Format in which the odML document is to be saved.
                    The default format is XML.
    """
    writer = ODMLWriter(backend)
    if "." not in filename.split(os.pathsep)[-1]:
        filename = filename + ".%s" % backend
    return writer.write_file(obj, filename)


def display(obj, backend="xml"):
    """
    Print an open odML document to the command line, formatted in the
    specified format.
    :param obj: odML document to be displayed.
    :param backend: Format in which the odML document is to be displayed.
                    The default format is XML.
    """
    writer = ODMLWriter(backend)
    print(writer.to_string(obj))
