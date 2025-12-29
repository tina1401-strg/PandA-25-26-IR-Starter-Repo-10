from typing import Dict, Any, Tuple, List, Iterator
import os
import json
from enum import Enum
from dataclasses import dataclass
from .models import Sonnet, SearchResults
import urllib.request
import urllib.error

# ---------- Configuration Class ----------
@dataclass(frozen=True)
class SettingSpec:
    attr: str
    allowed: Tuple[str, ...]
    label: str

class ParameterSettings(Enum):
    HIGHLIGHT_MODE = SettingSpec( attr=":highlight-mode", allowed=("DEFAULT", "GREEN"), label="Highlight mode set to")
    HIGHLIGHT = SettingSpec( attr=":highlight", allowed=("ON", "OFF"), label="Highlighting")
    SEARCH_MODE = SettingSpec( attr=":search-mode", allowed=("AND", "OR"), label="Search mode set to")

class Configuration:
    settings = (
        (ParameterSettings.HIGHLIGHT_MODE.name, ParameterSettings.HIGHLIGHT_MODE.value),
        (ParameterSettings.HIGHLIGHT.name, ParameterSettings.HIGHLIGHT.value),
        (ParameterSettings.SEARCH_MODE.name, ParameterSettings.SEARCH_MODE.value)
    )

    def __init__(self):
        # Default settings used at program startup.
        self.highlight = "ON"
        self.search_mode = "AND"
        self.highlight_mode = "DEFAULT"

    def copy(self):
        """
            Return a *shallow copy* of this configuration object.
            Useful when you want to pass config around without mutating the original.
        """
        copy = Configuration()
        copy.highlight = self.highlight
        copy.search_mode = self.search_mode
        copy.highlight_mode = self.highlight_mode
        return copy

    def update(self, other: Dict[str, Any]):

        if "highlight" in other and other["highlight"] in ["ON", "OFF"]:
            self.highlight = other["highlight"]

        if "search_mode" in other and other["search_mode"] in ["AND", "OR"]:
            self.search_mode = other["search_mode"]

        if "highlight_mode" in other and other["highlight_mode"] in ["DEFAULT", "GREEN"]:
            self.highlight_mode = other["highlight_mode"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "highlight": self.highlight,
            "search_mode": self.search_mode,
            "highlight_mode": self.highlight_mode,
        }

    @staticmethod
    def load() -> "Configuration":
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

    def save(self) -> None:
        config_file_path = module_relative_path("config.json")

        try:
            with open(config_file_path, "w") as config_file:
                json.dump(self.to_dict(), config_file, indent=4)
        except OSError:
            print(f"Writing config.json failed.")

    def check_settings(self, raw: str) -> bool:
        raw = raw.strip()

        for set_name, setting in self.settings:
            parts = raw.split(maxsplit=1)
            if parts[0] == setting.attr:
                if len(parts) == 2 and parts[1].strip().upper() in setting.allowed:
                    value = parts[1].strip().upper()
                    self.update({set_name.lower(): value})
                    print(setting.label, value)
                    self.save()
                else:
                    print(f"Usage: {setting.attr} {'|'.join(setting.allowed)}")

                return True

        return False

class Sonnets:

    def __init__(self):
        self.sonnets: List[Sonnet] = []

    def append(self, sonnet: Sonnet) -> None:
        self.sonnets.append(sonnet)

    def __getitem__(self, idx: int) -> Sonnet:
        return self.sonnets[idx]

    def __iter__(self) -> Iterator[Sonnet]:
        return iter(self.sonnets)

    def __len__(self) -> int:
        return len(self.sonnets)

    @staticmethod
    def fetch_from_api() -> List[dict]:
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

    @staticmethod
    def load() -> "Sonnets":

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
            sonnets = Sonnets.fetch_from_api()
            try:
                with open(sonnets_path, "w", encoding="utf-8") as f:
                    try:
                        json.dump(sonnets, f, indent=2, ensure_ascii=False)
                    except (TypeError, ValueError) as exc:
                        raise RuntimeError(f"Failed to serialize JSON for cache: {exc}") from exc
            except (OSError, IOError) as exc:
                raise RuntimeError(f"Failed to write cache file: {exc}") from exc

            print("Downloaded sonnets from PoetryDB.")

        s = Sonnets()
        for sonnet in sonnets:
            s.append(Sonnet(sonnet))

        return s

    def search(self, words: List[str], search_mode: str) -> "SearchResults":
        combined_results = SearchResults()

        for word in words:
            # Searching for the word in all sonnets
            results = SearchResults()
            [results.append(s.search_for(word)) for s in self]

            if len(combined_results) == 0:
                # No results yet. We store the first list of results in combined_results
                combined_results = results
            else:
                # We have an additional result, we have to merge the two results: loop all sonnets
                for i in range(len(combined_results)):
                    # Checking each sonnet individually
                    combined_result = combined_results[i]
                    result = results[i]

                    if search_mode == "AND":
                        if combined_result.matches > 0 and result.matches > 0:
                            # Only if we have matches in both results, we consider the sonnet (logical AND!)
                            combined_results[i] = combined_result.combine(result)
                        else:
                            # Not in both. No match!
                            combined_result.matches = 0
                    elif search_mode == "OR":
                        combined_results[i] = combined_result.combine(result)

        return combined_results

# ---------- Constants ----------
POETRYDB_URL = "https://poetrydb.org/author,title/Shakespeare;Sonnet"
CACHE_FILENAME = "sonnets.json"
DEFAULT_CONFIG = Configuration()

# ---------- Paths & Sonnet loading ----------
def module_relative_path(name: str) -> str:
    """Return absolute path for a file next to this module."""
    return os.path.join(os.path.dirname(__file__), name)
