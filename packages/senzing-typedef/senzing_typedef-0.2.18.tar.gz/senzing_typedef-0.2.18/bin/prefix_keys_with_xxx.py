#!/usr/bin/env python3

"""Read JSON from STDIN and prefix every JSON key with 'XXX_'"""

import json
import logging
import os
import sys

# Logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# --- Functions
# -----------------------------------------------------------------------------


def prefix_keys(obj, prefix="XXX_"):
    """Recursively prefix all JSON keys with the given prefix."""
    if isinstance(obj, dict):
        return {f"{prefix}{key}": prefix_keys(value, prefix) for key, value in obj.items()}
    if isinstance(obj, list):
        return [prefix_keys(item, prefix) for item in obj]
    return obj


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    # Prolog.

    logger.info("Begin %s", os.path.basename(__file__))

    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Prefix all keys
        output_data = prefix_keys(input_data)

        # Output JSON to stdout
        json.dump(output_data, sys.stdout, indent=2)
        print()  # Add newline at end

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Epilog.

    logger.info("End   %s", os.path.basename(__file__))
