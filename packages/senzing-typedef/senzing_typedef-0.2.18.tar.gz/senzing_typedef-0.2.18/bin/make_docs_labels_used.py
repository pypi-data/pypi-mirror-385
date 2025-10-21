#! /usr/bin/env python3

"""
Create docs/labels_used.json
"""

import json
import logging
import os
import pathlib

# Logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global variables.

CURRENT_PATH = pathlib.Path(__file__).parent.resolve()
INPUT_FILENAME = os.path.abspath(f"{CURRENT_PATH}/../senzingsdk-RFC8927.json")
OUTPUT_FILENAME = os.path.abspath(f"{CURRENT_PATH}/../docs/labels_used.json")

LABELS = {}

# -----------------------------------------------------------------------------
# --- Functions
# -----------------------------------------------------------------------------


def add_to_label(label, path):
    """Add description to LABELS dictionary."""
    if not label:
        return
    if label not in LABELS:
        LABELS[label] = []
    if path not in LABELS[label]:
        LABELS[label].append(path)


def recurse(path, json_key, json_object):
    """Use recursive descent"""

    # Determine new_path.

    new_path = ""
    if json_key not in ["", "definitions", "properties", None]:
        if len(path) > 0:
            new_path = f"{path}.{json_key}"
        else:
            new_path = json_key
    else:
        new_path = path

    # Recurse.

    match json_object:
        case dict():
            label = json_object.get("metadata", {}).get("label", None)
            add_to_label(label, new_path)
            for key, value in json_object.items():
                recurse(new_path, key, value)
        case list():
            for item in json_object:
                recurse(new_path, "list", item)


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

    INITIAL_PATH = ""
    recurse(INITIAL_PATH, "", DATA)

    # Write output file.

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as output_file:
        output_file.write(json.dumps(LABELS, sort_keys=True, indent=4))

    # Epilog.

    logger.info("End   %s", os.path.basename(__file__))
