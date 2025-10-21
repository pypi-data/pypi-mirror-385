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

    products = dmm_client.get_products(
        site="FANZA",
        keyword="ABP-477",
        floor="dvd",
        service="mono",
    )

    # access the list of products
    for product in products:
        print("Product ID:", product.content_id, end="\n")

    # access the total count of products found
    print("Total products found:", len(products), end="\n\n")

    # access the first product's details
    if products:
        first_product = products[0]
        print("First Product Details:")
        print(" - Title:", first_product.title)
        print(" - Image URL:", first_product.image_url)
        print(" - Floor Name:", first_product.floor_name)
        print(" - Price:", first_product.prices)
        print(" - Review:", first_product.review)
        print(" - Sample Images:", first_product.sample_image_url)
        print(" - Actresses: ", list(map(lambda a: a.name, first_product.actresses)))
        print(" - Genres: ", list(map(lambda g: (g.id, g.name), first_product.genres)))
        print(" - Maker ID:", first_product.makers)
        print(" - Series:", first_product.series)
        print(" - Maker Product:", first_product.maker_product)

    single_product = dmm_client.get_product_by_cid("mird00127", "FANZA")

    if single_product:
        print("\nSingle Product Details:")
        print(" - Title:", single_product.title)
        print(" - Image URL:", single_product.image_url)
        print(" - Floor Name:", single_product.floor_name)
        print(" - Price:", single_product.prices)
        print(" - Review:", single_product.review)
        print(" - Sample Images:", single_product.sample_image_url)
        print(" - Actresses: ", list(map(lambda a: a.name, single_product.actresses)))
        print(" - Genres: ", list(map(lambda g: (g.id, g.name), single_product.genres)))
        print(" - Maker ID:", single_product.makers)
        print(" - Series:", single_product.series)
        print(" - Maker Product:", single_product.maker_product)
    else:
        print("Product with content ID 'mird00127' not found.")

    maker_product = dmm_client.get_product_by_product_id("KEED-077", "FANZA")

    if maker_product:
        print("\nmaker Product Details:")
        print(" - Title:", maker_product.title)
        print(" - Image URL:", maker_product.image_url)
        print(" - Floor Name:", maker_product.floor_name)
        print(" - Price:", maker_product.prices)
        print(" - Review:", maker_product.review)
        print(" - Sample Images:", maker_product.sample_image_url)
        print(" - Actresses: ", list(map(lambda a: a.name, maker_product.actresses)))
        print(" - Genres: ", list(map(lambda g: (g.id, g.name), maker_product.genres)))
        print(" - Maker ID:", maker_product.makers)
        print(" - Series:", maker_product.series)
        print(" - Maker Product:", maker_product.maker_product)
    else:
        print("Product with product ID 'KEED-077' not found.")


if __name__ == "__main__":
    main()
