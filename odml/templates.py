"""
Handles (deferred) loading of odML templates
"""

import os
import sys
import tempfile
import threading
try:
    import urllib.request as urllib2
    from urllib.error import URLError
    from urllib.parse import urljoin

except ImportError:
    import urllib2
    from urllib2 import URLError
    from urlparse import urljoin

from datetime import datetime as dati
from datetime import timedelta
from hashlib import md5

from .tools.parser_utils import ParserException
from .tools.xmlparser import XMLReader


REPOSITORY_BASE = 'https://templates.g-node.org/'
REPOSITORY = urljoin(REPOSITORY_BASE, 'templates.xml')

CACHE_AGE = timedelta(days=1)
CACHE_DIR = "odml.cache"


# TODO after prototyping move functions common with
# terminologies to a common file.


def cache_load(url):
    """
    Load the url and store the file in a temporary cache directory.
    Subsequent requests for this url will use the cached version until
    the file is older than the CACHE_AGE.

    Exceptions are caught and not re-raised to enable loading of nested
    odML files without breaking if one of the child files is unavailable.

    :param url: location of an odML template XML file.
    :return: Local file location of the requested file.
    """

    filename = '.'.join([md5(url.encode()).hexdigest(), os.path.basename(url)])
    cache_dir = os.path.join(tempfile.gettempdir(), CACHE_DIR)

    # Create temporary folder if required
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
        except OSError:  # might happen due to concurrency
            if not os.path.exists(cache_dir):
                raise

    cache_file = os.path.join(cache_dir, filename)

    if not os.path.exists(cache_file) or \
            dati.fromtimestamp(os.path.getmtime(cache_file)) < (dati.now() - CACHE_AGE):
        try:
            data = urllib2.urlopen(url).read()
            if sys.version_info.major > 2:
                data = data.decode("utf-8")
        except (ValueError, URLError) as exc:
            msg = "Failed to load resource from '%s': %s" % (url, exc)
            exc.args = (msg,)  # needs to be a tuple
            raise exc

        with open(cache_file, "w") as local_file:
            local_file.write(str(data))

    return cache_file


class TemplateHandler(dict):
    """
    TemplateHandler facilitates synchronous and deferred
    loading, caching, browsing and importing of full or partial
    odML templates.
    """
    # Used for deferred loading
    loading = {}

    def browse(self, url):
        """
        Load, cache and pretty print an odML template XML file from a URL.

        :param url: location of an odML template XML file.
        :return: The odML document loaded from url.
        """
        doc = self.load(url)

        if not doc:
            raise ValueError("Failed to load resource from '%s'" % url)

        doc.pprint(max_depth=0)

        return doc

    def clone_section(self, url, section_name, children=True, keep_id=False):
        """
        Load a section by name from an odML template found at the provided URL
        and return a clone. By default it will return a clone with all child
        sections and properties as well as changed IDs for every entity.
        The named section has to be a root (direct) child of the referenced
        odML document.

        :param url: location of an odML template XML file.
        :param section_name: Unique name of the requested Section.
        :param children: Boolean whether the child entities of a Section will be
                         returned as well. Default is True.
        :param keep_id: Boolean whether all returned entities will keep the
                        original ID or have a new one assigned. Default is False.
        :return: The cloned odML section loaded from url.
        """
        doc = self.load(url)
        if not doc:
            raise ValueError("Failed to load resource from '%s'" % url)

        try:
            sec = doc[section_name]
        except KeyError:
            raise KeyError("Section '%s' not found in document at '%s'" % (section_name, url))

        return sec.clone(children=children, keep_id=keep_id)

    def load(self, url):
        """
        Load and cache an odML template from a URL.

        :param url: location of an odML template XML file.
        :return: The odML document loaded from url.
        """
        # Some feedback for the user when loading large or
        # nested (include) odML files.
        print("\nLoading file %s" % url)

        if url in self:
            doc = self[url]
        elif url in self.loading:
            self.loading[url].join()
            self.loading.pop(url, None)
            doc = self.load(url)
        else:
            doc = self._load(url)

        return doc

    def _load(self, url):
        """
        Cache loads an odML template for a URL and returns
        the result as a parsed odML document.

        :param url: location of an odML template XML file.
        :return: The odML document loaded from url.
                 It will silently return None, if any exceptions
                 occur to enable loading of nested odML files.
        """
        try:
            local_file = cache_load(url)
        except (ValueError, URLError):
            return None

        try:
            doc = XMLReader(filename=url, ignore_errors=True).from_file(local_file)
            doc.finalize()
        except ParserException as exc:
            print("Failed to load '%s' due to parser errors:\n %s" % (url, exc))
            return None

        self[url] = doc
        return doc

    def deferred_load(self, url):
        """
        Start a background thread to load an odML template from a URL.

        :param url: location of an odML template XML file.
        """
        if url in self or url in self.loading:
            return

        self.loading[url] = threading.Thread(target=self._load, args=(url,))
        self.loading[url].start()
