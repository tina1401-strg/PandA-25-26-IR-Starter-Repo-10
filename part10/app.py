#!/usr/bin/env python3
"""
Part 10 starter.

WHAT'S NEW IN PART 10
You will write two classes without detailed instructions! This is a refactoring, we are not adding new functionality 🙄.
"""

import time
from .constants import BANNER, HELP
from .file_utilities import Configuration, Sonnets

def main() -> None:
    print(BANNER)

    ### Load Config
    config = Configuration.load()

    ### Load sonnets (from cache or API)
    start = time.perf_counter()
    sonnets = Sonnets.load()
    elapsed = (time.perf_counter() - start) * 1000
    print(f"Loading sonnets took: {elapsed:.3f} [ms]\nLoaded {len(sonnets)} sonnets.")

    ### Input Request Handling
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

            if config.check_settings(raw):
                continue

            print("Unknown command. Type :help for commands.")
            continue

        # ---------- Query evaluation ----------
        words = raw.split()
        if not words:
            continue

        start = time.perf_counter()
        combined_results = sonnets.search(words, config.search_mode)
        elapsed_ms = (time.perf_counter() - start) * 1000

        combined_results.print(raw, config.highlight, config.highlight_mode, elapsed_ms)

if __name__ == "__main__":
    main()
