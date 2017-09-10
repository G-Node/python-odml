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
CACHE_DIR = os.path.join(tempfile.gettempdir(), "odml.cache")
FILE_MAP_FILE = os.path.join(CACHE_DIR, "odml_filemap.csv")
if not os.path.exists(CACHE_DIR):
    try:
        os.makedirs(CACHE_DIR)
    except OSError:  # might happen due to concurrency
        if not os.path.exists(CACHE_DIR):
            raise


def open_file_map():
    file_map = {}
    if not os.path.exists(FILE_MAP_FILE):
       return file_map
    else:
        with open(FILE_MAP_FILE, 'r') as f:
            for l in f.readlines():
                parts = l.strip().split(';')
                file_map[parts[0].strip()] = parts[1].strip()
    return file_map


def cache_load(url):
    """
    load the url and store it in a temporary cache directory
    subsequent requests for this url will use the cached version
    """
    filename = md5(url.encode()).hexdigest() + '__' + os.path.basename(url)
    cache_file = os.path.join(CACHE_DIR, filename)

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
        with open(FILE_MAP_FILE, 'a') as fm:
            fm.write(filename + "; " + url + "\n")
    return open(cache_file)


class Terminologies(dict):
    loading = {}

    def load(self, url="http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml"):
        """
        load and cache a terminology-url

        returns the odml-document for the url
        """
        if url in self:
            return self[url]

        encode_name =  md5(url.encode()).hexdigest() + '__' + os.path.basename(url)
        if encode_name in self:
            return self[encode_name]

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

    def cached_files(self):
        filelist = [ f for f in os.listdir(CACHE_DIR) if \
                     (f.endswith(".xml") and os.path.isfile(os.path.join(CACHE_DIR, f)))]
        return filelist

    def show_cache(self):
        print("terminology %s \t updated"%(19*" "))
        print(60*"-")
        for f in self.cached_files():
            cache_file = os.path.join(CACHE_DIR, f)
            file_timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file))
            disp_name = '_'.join(f.split('__')[1:])
            if len(disp_name) > 30:
                disp_name = disp_name[:16] + "..."
            if len(disp_name) < 30:
                disp_name = disp_name + (30 -len(disp_name)) * " "
            print(" %s \t %s"%(disp_name, file_timestamp))

    def clear_cache(self):
        filelist = self.cached_files();
        for f in filelist:
            os.remove(os.path.join(CACHE_DIR, f))
        if os.path.exists(FILE_MAP_FILE):
            os.remove(FILE_MAP_FILE)

    def from_cache(self):
        file_list = self.cached_files();
        file_map = open_file_map();
        for f in file_map:
            if file_map[f] not in self:
                self.load(file_map[f])
        
terminologies = Terminologies()
load = terminologies.load
deferred_load = terminologies.deferred_load




if __name__ == "__main__":
    from IPython import embed
    print ("Terminologies!")
    # t.load('http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml')
    embed()
    # t.load('http://portal.g-node.org/odml/terminologies/v1.0/analysis/power_spectrum.xml')

