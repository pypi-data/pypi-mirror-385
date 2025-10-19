import time

import requests

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

        user_uprn = kwargs.get("uprn")
        check_uprn(user_uprn)
        bindata = {"bins": []}

        SESSION_URL = "https://mycouncil.milton-keynes.gov.uk/authapi/isauthenticated?uri=https%253A%252F%252Fmycouncil.milton-keynes.gov.uk%252Fen%252Fservice%252FWaste_Collection_Round_Checker&hostname=mycouncil.milton-keynes.gov.uk&withCredentials=true"

        API_URL = "https://mycouncil.milton-keynes.gov.uk/apibroker/runLookup"

        data = {
            "formValues": {"Section 1": {"uprnCore": {"value": user_uprn}}},
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://mycouncil.milton-keynes.gov.uk/fillform/?iframe_id=fillform-frame-1&db_id=",
        }
        s = requests.session()
        r = s.get(SESSION_URL)
        r.raise_for_status()
        session_data = r.json()
        sid = session_data["auth-session"]
        params = {
            "id": "64d9feda3a507",
            "repeat_against": "",
            "noRetry": "false",
            "getOnlyTokens": "undefined",
            "log_id": "",
            "app_name": "AF-Renderer::Self",
            # unix_timestamp
            "_": str(int(time.time() * 1000)),
            "sid": sid,
        }

        r = s.post(API_URL, json=data, headers=headers, params=params)
        r.raise_for_status()

        data = r.json()
        rows_data = data["integration"]["transformed"]["rows_data"]
        if not isinstance(rows_data, dict):
            raise ValueError("Invalid data returned from API")

        # Extract each service's relevant details for the bin schedule
        for item in rows_data.values():
            dict_data = {
                "type": item["AssetTypeName"],
                "collectionDate": datetime.strptime(
                    item["NextInstance"], "%Y-%m-%d"
                ).strftime(date_format),
            }
            bindata["bins"].append(dict_data)

        return bindata
