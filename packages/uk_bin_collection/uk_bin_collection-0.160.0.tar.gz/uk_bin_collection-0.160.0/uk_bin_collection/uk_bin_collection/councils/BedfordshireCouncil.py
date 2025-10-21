from datetime import datetime

import requests
from bs4 import BeautifulSoup

from uk_bin_collection.uk_bin_collection.common import *
from uk_bin_collection.uk_bin_collection.get_bin_data import AbstractGetBinDataClass


class CouncilClass(AbstractGetBinDataClass):
    """
    Concrete classes have to implement all abstract operations of the
    base class. They can also override some operations with a default
    implementation.
    """

    def parse_data(self, page: str, **kwargs) -> dict:
        user_uprn = kwargs.get("uprn")
        user_postcode = kwargs.get("postcode")

        check_uprn(user_uprn)
        check_postcode(user_postcode)

        # Start a new session to walk through the form
        requests.packages.urllib3.disable_warnings()
        s = requests.Session()

        headers = {
            "Origin": "https://www.centralbedfordshire.gov.uk",
            "Referer": "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_day",

            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.7968.1811 Mobile Safari/537.36",
        }

        files = {
            "postcode": (None, user_postcode),
            "address": (None, user_uprn),
        }

        response = requests.post(
            "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_day#my_bin_collections",
            headers=headers,
            files=files,
        )

        # Make that BS4 object and use it to prettify the response
        soup = BeautifulSoup(response.content, features="html.parser")
        soup.prettify()

        collections_div = soup.find(id="collections")

        # Get the collection items on the page and strip the bits of text that we don't care for
        collections = []
        for bin in collections_div.find_all("h3"):
            next_bin = bin.next_sibling

            while next_bin.name != "h3" and next_bin.name != "p":
                if next_bin.name != "br":
                    collection_date = datetime.strptime(bin.text, "%A, %d %B %Y")
                    collections.append((next_bin, collection_date))
                next_bin = next_bin.next_sibling

        # Sort the collections by date order rather than bin type, then return as a dictionary (with str date)
        ordered_data = sorted(collections, key=lambda x: x[1])
        data = {"bins": []}
        for item in ordered_data:
            dict_data = {
                "type": item[0],
                "collectionDate": item[1].strftime(date_format),
            }
            data["bins"].append(dict_data)

        return data
