#!/usr/bin/env python3

# pylint: disable=missing-function-docstring,missing-module-docstring,too-many-statements
# pylint: disable=duplicate-code

"""
Example usage of the py-dmm library.
"""

import os
import sys

# Add the parent directory to the path to import py_dmm
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from py_dmmjp import DMMClient


def main() -> None:
    api_key = os.getenv("DMM_API_KEY")
    affiliate_key = os.getenv("DMM_AFFILIATE_KEY")

    if not api_key:
        print("Please set the DMM_API_KEY environment variable")
        return

    if not affiliate_key:
        print("Please set the DMM_AFFILIATE_KEY environment variables")
        return

    dmm_client = DMMClient(api_key=api_key, affiliate_id=affiliate_key)

    print(dmm_client)

    actresses = dmm_client.get_actresses()

    # access the list of actresses
    for actress in actresses:
        print("Actress ID:", actress.id, end="\n")
        print(f"Actress Name: {actress.name}" f" ({actress.ruby})", end="\n\n")

    # access the total count of actresses found
    print("Total actresses found:", len(actresses), end="\n\n")


if __name__ == "__main__":
    main()
