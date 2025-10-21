#! /usr/bin/env python3
# pylint: disable=duplicate-code

"""
For more information, visit https://jsontypedef.com/docs/python-codegen/
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
TESTDATA_DIRECTORY = os.path.abspath(f"{CURRENT_PATH}/../testdata")
OUTPUT_DIRECTORY = f"{TESTDATA_DIRECTORY}/responses"

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def append_files(source_directory, target_directory):
    """Append contents from source_directory into the files of the target_directory."""
    filenames = os.listdir(source_directory)
    for filename in filenames:
        with open(os.path.join(source_directory, filename), "r", encoding="utf-8") as source_file:
            source_lines = source_file.read()
        with open(os.path.join(target_directory, filename), "a", encoding="utf-8") as target_file:
            target_file.write(source_lines)


def normalize_files(directory):
    """Deduplicate and sort JSON lines."""
    for root, _, files in os.walk(directory):
        for file in files:
            remove_duplicate_lines(os.path.join(root, file))


def remove_duplicate_lines(input_filepath, output_filepath=None):
    """
    Removes duplicate lines from a text file.

    Args:
        input_filepath (str): The path to the input file.
        output_filepath (str, optional): The path to the output file.
        If None, the input file will be overwritten.
    """
    unique_lines = set()
    try:
        with open(input_filepath, "r", encoding="utf-8") as infile:
            for line in infile:
                line = line.strip()
                if len(line) > 0:
                    line_as_dict = json.loads(line)
                    unique_lines.add(json.dumps(line_as_dict, sort_keys=True))
    except FileNotFoundError:
        logger.warning("Error: Input file '%s' not found.", input_filepath)
        return

    if output_filepath is None:
        output_filepath = input_filepath

    try:
        with open(output_filepath, "w", encoding="utf-8") as outfile:
            for line in sorted(list(unique_lines)):
                outfile.write(f"{line}\n")
        logger.debug("Duplicates removed in '%s'.", output_filepath)
    except IOError:
        logger.error("Error: Could not write to output file '%s'.", output_filepath)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    # Prolog.

    logger.info("Begin %s", os.path.basename(__file__))

    # Process data.

    DIRECTORIES = ["responses_static", "responses_truthsets", "responses_th4"]
    for DIRECTORY in DIRECTORIES:
        append_files(os.path.join(TESTDATA_DIRECTORY, DIRECTORY), OUTPUT_DIRECTORY)

    normalize_files(OUTPUT_DIRECTORY)

    # Epilog.

    logger.info("End   %s", os.path.basename(__file__))
