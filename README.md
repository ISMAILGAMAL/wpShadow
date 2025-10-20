# wpShadow

**wpShadow** is a Python utility designed to download, manage, and monitor a large collection of popular WordPress plugins. It uses multi-threading for speed and a local cache to only download plugins that are new or have been updated since the last run.

This tool is useful for security researchers, bug bounty hunters, or developers who need a large, locally-stored dataset of recent WordPress plugin code for **static analysis** or **vulnerability research**.


## Installation & Setup

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/ISMAILGAMAL/wpShadow.git
    cd wpShadow
    ```

2.  **Ensure Dependencies are Met:**

    ```bash
    pip install requests
    ```

3.  **Directory Structure:**
    The script will automatically create the following directories upon first run:

    ```
    .
    ├── wpshadow.py      # The main script
    ├── cache.json        # Plugin cache file (created on first run)
    ├── Zips/             # Downloaded .zip files are stored here
    └── Plugins/          # Extracted plugin source code is stored here
    ```

-----

## Usage

Simply execute the Python script from your terminal:

```bash
python3 wpshadow.py
```

### What Happens When You Run It:

1.  **Metadata Fetching:** The script contacts the WordPress API to get the slugs, download links, and last updated timestamps for the top 1,800 plugins.
2.  **Downloading & Caching:**
      * For each plugin, it checks the `cache.json` file.
      * If the plugin is **not in the cache** or the **API timestamp is newer** than the cached one, the plugin is downloaded and extracted.
      * The newly downloaded plugin's details are then saved to the cache.
3.  **Extraction:** Updated plugins are automatically extracted into the `Plugins/` directory, overwriting any previous version to ensure you always have the freshest code.

-----

## Cleaning Up

If you need to force a full re-download, or simply free up disk space, you can manually delete the generated directories and cache file.

| Command | Action |
| :--- | :--- |
| `rm -rf Plugins/` | Removes all extracted plugin source code. |
| `rm -rf Zips/` | Removes all downloaded plugin ZIP files. |
| `rm cache.json` | Resets the cache, forcing the script to re-download all plugins on the next run. |

-----

## Contribution

Feel free to open an issue or submit a pull request if you have suggestions for performance improvements, feature additions, or bug fixes. I may or may not expand the tool into something bigger that helps with bug hunting on wordpress plugins.