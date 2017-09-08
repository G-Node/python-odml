"""
Handles (deferred) loading of terminology data and access to it
for odML documents
"""

import os
import tempfile
import datetime
import odml.tools.xmlparser
from hashlib import md5
py3 = True

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

import threading

CACHE_AGE = datetime.timedelta(days=14)


def cache_load(url):
    """
    load the url and store it in a temporary cache directory
    subsequent requests for this url will use the cached version
    """
    filename = md5(url.encode()).hexdigest() + os.path.basename(url)
    cache_dir = os.path.join(tempfile.gettempdir(), "odml.cache")
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
        except OSError:  # might happen due to concurrency
            if not os.path.exists(cache_dir):
                raise
    cache_file = os.path.join(cache_dir, filename)
    if not os.path.exists(cache_file) \
       or datetime.datetime.fromtimestamp(os.path.getmtime(cache_file)) < \
       datetime.datetime.now() - CACHE_AGE:
        try:
            data = urlopen(url).read().decode("utf-8")
        except Exception as e:
            print("Failed loading '%s': %s" % (url, e))
            return

        fp = open(cache_file, "w")
        fp.write(data)
        fp.close()

    return open(cache_file)


class Terminologies(dict):
    loading = {}

    def load(self, url):
        """
        load and cache a terminology-url

        returns the odml-document for the url
        """
        if url in self:
            return self[url]

        if url in self.loading:
            self.loading[url].join()
            self.loading.pop(url, None)
            return self.load(url)

        return self._load(url)

    def _load(self, url):
        # TODO also cache the data locally on disk
        # if url.startswith("http"): return None
        fp = cache_load(url)
        if fp is None:
            print("Did not successfully load '%s'" % url)
            return
        try:
            term = odml.tools.xmlparser.XMLReader(filename=url, ignore_errors=True).fromFile(fp)
            term.finalize()
        except odml.tools.xmlparser.ParserException as e:
            print("Failed to load %s due to parser errors" % url)
            print(' "%s"' % e)
            term = None
        self[url] = term
        return term

    def deferred_load(self, url):
        """
        start a thread to load the terminology in background
        """
        if url in self or url in self.loading:
            return
        self.loading[url] = threading.Thread(target=self._load, args=(url,))
        self.loading[url].start()

    def show_cache(self):
        cache_dir = os.path.join(tempfile.gettempdir(), "odml.cache")
        onlyfiles = [f for f in os.listdir(cache_dir) if os.path.isfile(os.path.join(cache_dir, f))]
        print("terminology %s \t updated"%(19*" "))
        print(60*"-")
        for f in onlyfiles:
            cache_file = os.path.join(cache_dir, f)
            file_timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file))
            disp_name = '_'.join(f.split('__')[1:])
            if len(disp_name) > 30:
                disp_name = disp_name[:16] + "..."
            if len(disp_name) < 30:
                disp_name = disp_name + (30 -len(disp_name)) * " "
            print(" %s \t %s"%(disp_name, file_timestamp))


terminologies = Terminologies()
load = terminologies.load
deferred_load = terminologies.deferred_load



class TerminologyManager(object) :

    def __init__(self, terminology_url='https://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml'):
        self.t = Terminologies()
        self.types_map = {}
        if (terminology_url is not None):
            self.load(terminology_url)

    def load(self, url):
        self.t.load(url)
        self.__parse_terminology(url, self.t[url])

    def type_list(self):
        types = []
        for k in self.t.itervalues():
            temp = [s.type for s in k.itersections()]
            types.extend(temp)
        return types

    def __parse_terminology(self, url=None, doc=None):
        if url is None or doc is None:
            print("some is None")
            return
        for s in doc.itersections():
            if s.type in self.types_map.keys():
                type_map = self.types_map[s.type]
                if url in type_map.keys() and s.get_path() in type_map.itervalues():
                    continue
                type_map[url] = s.get_path()
            else:
                self.types_map[s.type] = {url: s.get_path()}


if __name__ == "__main__":
    from IPython import embed
    print ("Terminologies!")
    terms = TerminologyManager()
    
    # t = Terminologies()
    # t.load('http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml')
    embed()
    # t.load('http://portal.g-node.org/odml/terminologies/v1.0/analysis/power_spectrum.xml')

