#! /usr/bin/env python3

"""
Create docs/json_key_descriptions.json
"""

import json
import logging
import os
import pathlib

# Logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global variables.

JSON_KEYS = {}

CURRENT_PATH = pathlib.Path(__file__).parent.resolve()
INPUT_FILENAME = os.path.abspath(f"{CURRENT_PATH}/../senzingsdk-RFC8927.json")
OUTPUT_FILENAME = os.path.abspath(f"{CURRENT_PATH}/../docs/json_key_descriptions.json")

# -----------------------------------------------------------------------------
# --- Functions
# -----------------------------------------------------------------------------


def add_description(key, description):
    """Add description to JSON_KEYS dictionary."""
    if (not description) and (key not in JSON_KEYS):
        return
    if key not in JSON_KEYS:
        JSON_KEYS[key] = []
    normalized_description = as_string(description)
    if normalized_description not in JSON_KEYS[key]:
        JSON_KEYS[key].append(normalized_description)


def as_string(candidate):
    """Change None to string."""
    if not candidate:
        return ""
    return candidate


def recurse(json_key, json_object):
    """Use recursive descent"""
    match json_object:
        case dict():
            add_description(json_key, json_object.get("metadata", {}).get("description", None))
            for key, value in json_object.items():
                recurse(key, value)
        case list():
            for item in json_object:
                recurse("list", item)


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    # Prolog.

    logger.info("Begin %s", os.path.basename(__file__))

    # Read input file.

    with open(INPUT_FILENAME, "r", encoding="utf-8") as input_file:
        DATA = json.load(input_file)

    # Process data.

    recurse("", DATA)

    # Write output file.

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as output_file:
        output_file.write(json.dumps(JSON_KEYS, sort_keys=True, indent=4))

    # Epilog.

    logger.info("End   %s", os.path.basename(__file__))
