import os
import json

INSTALL_PATH = os.path.dirname(__file__)

with open(os.path.join(INSTALL_PATH, "info.json")) as infofile:
    infodict = json.load(infofile)

VERSION = infodict["VERSION"]
FORMAT_VERSION = infodict["FORMAT_VERSION"]
AUTHOR = infodict["AUTHOR"]
COPYRIGHT = infodict["COPYRIGHT"]
CONTACT = infodict["CONTACT"]
HOMEPAGE = infodict["HOMEPAGE"]
CLASSIFIERS = infodict["CLASSIFIERS"]
