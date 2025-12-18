#!/usr/bin/env python3
"""
Part 10 starter.

WHAT'S NEW IN PART 10
You will write two classes without detailed instructions! This is a refactoring, we are not adding new functionality 🙄.
"""

# ToDo 0: You will need to move and change some imports
from typing import List
import json
import os
import time
import urllib.request
import urllib.error

from .constants import BANNER, HELP, POETRYDB_URL, CACHE_FILENAME
from .models import Sonnet, SearchResult, Configuration, LineMatch

def print_results(
    query: str,
    results: List[SearchResult],
    highlight: bool,
    query_time_ms: float | None = None,
) -> None:
    total_docs = len(results)
    matched = [r for r in results if r.matches > 0]

    line = f'{len(matched)} out of {total_docs} sonnets contain "{query}".'
    if query_time_ms is not None:
        line += f" Your query took {query_time_ms:.2f}ms."
    print(line)

    for idx, r in enumerate(matched, start=1):
        r.print(idx, highlight, total_docs)


# ---------- Paths & data loading ----------
# ToDo 0: Move to file_utilities.py
def module_relative_path(name: str) -> str:
    """Return absolute path for a file next to this module."""
    return os.path.join(os.path.dirname(__file__), name)

# ToDo 0: Move to file_utilities.py
def fetch_sonnets_from_api() -> List[Sonnet]:
    """
    Call the PoetryDB API (POETRYDB_URL), decode the JSON response and
    convert it into a list of dicts.

    - Use only the standard library (urllib.request).
    - PoetryDB returns a list of poems.
    - You can add error handling: raise a RuntimeError (or print a helpful message) if something goes wrong.
    """
    sonnets = []

    try:
        with urllib.request.urlopen(POETRYDB_URL, timeout=10) as response:
            status = getattr(response, "status", None)
            if status not in (None, 200):
                raise RuntimeError(f"Request failed with HTTP status {status}")

            try:
                sonnets = json.load(response)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Failed to decode JSON: {exc}") from exc

    except (urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError) as exc:
        raise RuntimeError(f"Network-related error occurred: {exc}") from exc

    return sonnets

# ToDo 0: Move to file_utilities.py
def load_sonnets() -> List[Sonnet]:
    """
    Load Shakespeare's sonnets with caching.

    Behaviour:
      1. If 'sonnets.json' already exists:
           - Print: "Loaded sonnets from cache."
           - Return the data.
      2. Otherwise:
           - Call fetch_sonnets_from_api() to load the data.
           - Print: "Downloaded sonnets from PoetryDB."
           - Save the data (pretty-printed) to CACHE_FILENAME.
           - Return the data.
    """
    sonnets_path = module_relative_path(CACHE_FILENAME)

    if os.path.exists(sonnets_path):
        try:
            with open(sonnets_path, "r", encoding="utf-8") as f:
                try:
                    sonnets = json.load(f)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"Corrupt cache file (invalid JSON): {exc}") from exc
        except (OSError, IOError) as exc:
            raise RuntimeError(f"Failed to read cache file: {exc}") from exc

        print("Loaded sonnets from the cache.")
    else:
        sonnets = fetch_sonnets_from_api()
        try:
            with open(sonnets_path, "w", encoding="utf-8") as f:
                try:
                    json.dump(sonnets, f, indent=2, ensure_ascii=False)
                except (TypeError, ValueError) as exc:
                    raise RuntimeError(f"Failed to serialize JSON for cache: {exc}") from exc
        except (OSError, IOError) as exc:
            raise RuntimeError(f"Failed to write cache file: {exc}") from exc

        print("Downloaded sonnets from PoetryDB.")

    return [Sonnet(data) for data in sonnets]
# ------------------------- Config handling ---------------------------------
# ToDo 0: Move to file_utilities.py
DEFAULT_CONFIG = Configuration()

# ToDo 0: Move to file_utilities.py
def load_config() -> Configuration:
    config_file_path = module_relative_path("config.json")

    cfg = DEFAULT_CONFIG.copy()
    try:
        with open(config_file_path) as config_file:
            cfg.update(json.load(config_file))
    except FileNotFoundError:
        # File simply doesn't exist yet → quiet, just use defaults
        print("No config.json found. Using default configuration.")
        return cfg
    except json.JSONDecodeError:
        # File exists but is not valid JSON
        print("config.json is invalid. Using default configuration.")
        return cfg
    except OSError:
        # Any other OS / IO problem (permissions, disk issues, etc.)
        print("Could not read config.json. Using default configuration.")
        return cfg

    return cfg

# ToDo 0: Move to file_utilities.py
def save_config(cfg: Configuration) -> None:
    config_file_path = module_relative_path("config.json")

    try:
        with open(config_file_path, "w") as config_file:
            json.dump(cfg.to_dict(), config_file, indent=4)
    except OSError:
        print(f"Writing config.json failed.")

# ---------- CLI loop ----------

def main() -> None:
    print(BANNER)
    # ToDo 0: Depending on how your imports look, you may need to adapt the call to load_config()
    config = load_config()

    # Load sonnets (from cache or API)
    start = time.perf_counter()
    # ToDo 0: Depending on how your imports look, you may need to adapt the call to load_sonnets()
    sonnets = load_sonnets()

    elapsed = (time.perf_counter() - start) * 1000
    print(f"Loading sonnets took: {elapsed:.3f} [ms]")

    print(f"Loaded {len(sonnets)} sonnets.")

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue

        # commands
        if raw.startswith(":"):
            if raw == ":quit":
                print("Bye.")
                break

            if raw == ":help":
                print(HELP)
                continue

            # ToDo 2: You realize that the three settings 'highlight', 'search-mode', and 'hl-mode' have a lot
            #  in common. Wrap the common behavior in a class and use this class three times. If you want, you can
            #  make in an enum 😊.

            if raw.startswith(":highlight"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].lower() in ("on", "off"):
                    config.highlight = parts[1].lower() == "on"
                    print("Highlighting", "ON" if config.highlight else "OFF")
                    # ToDo 0: Depending on how your imports look, you may need to adapt the call to save_config()
                    # ToDo 0: You need to adapt the call to save_config
                    save_config(config)
                else:
                    print("Usage: :highlight on|off")
                continue

            if raw.startswith(":search-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("AND", "OR"):
                    config.search_mode = parts[1].upper()
                    print("Search mode set to", config.search_mode)
                    # ToDo 0: You need to adapt the call to save_config
                    save_config(config)
                else:
                    print("Usage: :search-mode AND|OR")
                continue

            # ToDo 0: A new setting is added here. It's command string is ':hl-mode'.

            print("Unknown command. Type :help for commands.")
            continue

        # ---------- Query evaluation ----------
        words = raw.split()
        if not words:
            continue

        start = time.perf_counter()

        # ToDo 1: Extract the search - basically everything until the end of the time measurement in a new class.
        #  Find a good name for that class. Make this class encapsulate our list of sonnets!
        words = raw.split()

        combined_results = []

        for word in words:
            # Searching for the word in all sonnets
            results = [s.search_for(word) for s in sonnets]

            if not combined_results:
                # No results yet. We store the first list of results in combined_results
                combined_results = results
            else:
                # We have an additional result, we have to merge the two results: loop all sonnets
                for i in range(len(combined_results)):
                    # Checking each sonnet individually
                    combined_result = combined_results[i]
                    result = results[i]

                    if config.search_mode == "AND":
                        if combined_result.matches > 0 and result.matches > 0:
                            # Only if we have matches in both results, we consider the sonnet (logical AND!)
                            combined_results[i] = combined_result.combine_with(result)
                        else:
                            # Not in both. No match!
                            combined_result.matches = 0
                    elif config.search_mode == "OR":
                        combined_results[i] = combined_result.combine_with(result)

        # Initialize elapsed_ms to contain the number of milliseconds the query evaluation took
        elapsed_ms = (time.perf_counter() - start) * 1000

        # ToDo 0: You will need to pass the new setting, the highlight_mode to print_results and use it there
        print_results(raw, combined_results, config.highlight, elapsed_ms)

if __name__ == "__main__":
    main()
