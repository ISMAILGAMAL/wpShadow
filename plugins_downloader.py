from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import threading
import time
from typing import List
import requests, os
import zipfile, json

NUM_PLUGINS = 1800
PER_PAGE = 100
BASE_DIR = os.path.dirname(__file__)
PLUGINS_PATH = os.path.join(BASE_DIR, "Plugins")
ZIPS_PATH = os.path.join(BASE_DIR, "Zips")
CACHE_FILE = os.path.join(BASE_DIR, "cache.json")
CACHE_LOCK = threading.Lock()

os.makedirs(PLUGINS_PATH, exist_ok=True)
os.makedirs(ZIPS_PATH, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "Wp-Shadow"})

# Just something i wanted to try :)
class Spinner:
    def __init__(self, message):
        self.message = message
        self.done = False
        self.frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']

    def start(self):
        def spin():
            i = 0
            while not self.done:
                frame = self.frames[i % len(self.frames)]
                sys.stdout.write(f"\r\033[36m{frame}\033[0m {self.message}")
                sys.stdout.flush()
                i += 1
                time.sleep(0.08)
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
            sys.stdout.flush()

        threading.Thread(target=spin, daemon=True).start()
        return self

    __enter__ = start

    def updateMessage(self, message):
        self.message = message

    def stop(self):
        self.done = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class Plugin:
    def __init__(self, slug, download_link, last_updated):
        self.slug = slug
        self.download_link = download_link
        self.last_updated = last_updated

    def downloadPluginZip(self):
        with session.get(self.download_link, stream=True) as r:
            zip_path = os.path.join(ZIPS_PATH, f"{self.slug}.zip")
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)

    def checkCached(self):
        if not os.path.isfile(CACHE_FILE):
            return False
        
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
        
        if data.get(self.slug, None) != self.last_updated:
            return False
        return True

    def cachePlugin(self):
        with CACHE_LOCK:
            try:
                if not os.path.isfile(CACHE_FILE):
                    with open(CACHE_FILE, 'w') as f:
                        json.dump({self.slug: self.last_updated}, f, indent=2)
                    return True
                
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                data.update({self.slug: self.last_updated})

                with open(CACHE_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                return True
            except Exception as e:
                print(f"An error occured while caching the file: {e}")
                return False

    def unzipPlugin(self):
        zip_path = os.path.join(ZIPS_PATH, f"{self.slug}.zip")
        zip = zipfile.ZipFile(zip_path)
        zip.extractall(PLUGINS_PATH)

def getPluginsMetadata():
    num_fetched = 0; page = 1
    plugins = []

    with Spinner("") as spinner:
        while num_fetched < NUM_PLUGINS:
            spinner.updateMessage(f"Fetching Plugins Metadata {num_fetched}/{NUM_PLUGINS}")

            res = session.get("https://api.wordpress.org/plugins/info/1.2/", params={
                "action" : "query_plugins",
                "per_page" : min(PER_PAGE, NUM_PLUGINS - num_fetched),
                "browse" : "popular",
                "page" : page
            })
            page += 1

            try:
                res.raise_for_status()
                res_json = res.json()
                num_fetched += len(res_json.get("plugins"))
            except Exception as e:
                print(f"An error occured: {e}" )

            for plugin in res_json.get("plugins"):
                slug = plugin.get("slug")
                download_link = plugin.get("download_link")
                last_updated = plugin.get("last_updated")
                plugins.append(Plugin(slug, download_link, last_updated))

    return plugins


def handle_plugin(plugin):
    if not plugin.checkCached():
        plugin.downloadPluginZip()
        plugin.unzipPlugin()
        plugin.cachePlugin()


def downloadUpdatedPlugins(plugins: List[Plugin]):
    with Spinner("") as spinner:
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(handle_plugin, p) for p in plugins]
            for i, f in enumerate(as_completed(futures)):
                try:
                    spinner.updateMessage(f"Downloading uncached or updated plugins {i}/{NUM_PLUGINS}")
                    f.result()  # raise exception if thread failed
                except Exception as e:
                    print(f"\nError downloading plugin: {e}")



def main():
    plugins = getPluginsMetadata()
    downloadUpdatedPlugins(plugins)

if __name__ == "__main__":
    main()