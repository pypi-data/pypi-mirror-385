# This script pulls (in one hit) the
# data from Warick District Council Bins Data
from bs4 import BeautifulSoup
from uk_bin_collection.uk_bin_collection.common import *
from uk_bin_collection.uk_bin_collection.get_bin_data import AbstractGetBinDataClass


# import the wonderful Beautiful Soup and the URL grabber
class CouncilClass(AbstractGetBinDataClass):
    """
    Concrete classes have to implement all abstract operations of the
    base class. They can also override some operations with a default
    implementation.
    """

    def parse_data(self, page: str, **kwargs) -> dict:
        # Make a BS4 object
        soup = BeautifulSoup(page.text, features="html.parser")
        soup.prettify()

        data = {"bins": []}

        for bins in soup.select('div[class*="service-item"]'):
            bin_type = bins.div.h3.text.strip()
            binCollection = datetime.strptime(
                bins.select("div > p")[1].get_text(strip=True), "%A, %d %B %Y"
            )
            # binImage = "https://myaccount.stockport.gov.uk" + bins.img['src']

            # batteries don't have a service date or other
            # info associated with them.
            if binCollection:
                dict_data = {
                    "type": bin_type,
                    "collectionDate": binCollection.strftime(date_format),
                }
                data["bins"].append(dict_data)

        return data
