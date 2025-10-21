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

    floor_list = dmm_client.get_floors()

    for site in floor_list:
        print(f"Site: {site.name} ({site.code})")

        for service in site.services:
            print(f"  Service: {service.name} ({service.code})")

            for floor in service.floors:
                print(f"    Floor: {floor.name} ({floor.code})")


if __name__ == "__main__":
    main()
