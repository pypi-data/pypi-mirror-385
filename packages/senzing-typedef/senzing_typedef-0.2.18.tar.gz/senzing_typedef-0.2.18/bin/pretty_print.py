#! /usr/bin/env python3
# pylint: disable=duplicate-code

"""
Pretty print the JSON.
"""

import json
import logging
import os
import pathlib

# Logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global variables.

BLACK_LIST = [
    "description",
    "elements",
    "goType",
    "metadata",
    "properties",
    "ref",
    "optionalproperties",
    "type",
]

CURRENT_PATH = pathlib.Path(__file__).parent.resolve()
INPUT_FILENAME = os.path.abspath(f"{CURRENT_PATH}/../senzingsdk-RFC8927.json")
OUTPUT_FILENAME = os.path.abspath(f"{CURRENT_PATH}/../senzingsdk-RFC8927-pretty.json")

# -----------------------------------------------------------------------------
# --- Helpers
# -----------------------------------------------------------------------------


def recurse(prefix, an_object):
    """Recurse though the dictionary, beautifying as it goes."""
    for key, value in an_object.items():
        if isinstance(value, dict):
            recurse(f"{prefix}.{key}", value)
            # if key not in BLACK_LIST:
            #     if "metadata" not in value:
            #         value["metadata"] = {}
            #     if "description" not in value.get("metadata"):
            #         value["metadata"]["description"] = "No description."
            #     if "goType" not in value.get("metadata"):
            #         if value.get("type") == "int32":
            #             value["metadata"]["goType"] = "int64"


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    # Prolog.

    logger.info("Begin %s", os.path.basename(__file__))

    # Read JSON from file.

    with open(INPUT_FILENAME, "r", encoding="utf-8") as input_file:
        DATA = json.load(input_file)

    # Recurse through dictionary.

    # recurse("definitions", DATA.get("definitions"))

    # Write JSON to file.

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as output_file:
        json.dump(DATA, output_file, indent=4, sort_keys=True)

    # Epilog.

    logger.info("End   %s", os.path.basename(__file__))
