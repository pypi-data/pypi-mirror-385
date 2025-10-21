import re
import time

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

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

        collection_day = kwargs.get("paon")
        garden_collection_week = kwargs.get("postcode")
        garden_collection_day = kwargs.get("uprn")
        bindata = {"bins": []}

        days_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        garden_week = ["Week 1", "Week 2"]

        refusestartDate = datetime(2024, 11, 4)
        recyclingstartDate = datetime(2024, 11, 11)

        offset_days = days_of_week.index(collection_day)
        offset_days_garden = days_of_week.index(garden_collection_day)
        if garden_collection_week:
            garden_collection = garden_week.index(garden_collection_week)

        refuse_dates = get_dates_every_x_days(refusestartDate, 14, 28)
        recycling_dates = get_dates_every_x_days(recyclingstartDate, 14, 28)

        bank_holidays = [
            ("25/12/2024", 2),
            ("26/12/2024", 2),
            ("27/12/2024", 3),
            ("30/12/2024", 1),
            ("31/12/2024", 2),
            ("01/01/2025", 2),
            ("02/01/2025", 2),
            ("03/01/2025", 3),
            ("06/01/2025", 1),
            ("07/01/2025", 1),
            ("08/01/2025", 1),
            ("09/01/2025", 1),
            ("10/01/2025", 1),
            ("18/04/2025", 1),
            ("21/04/2025", 1),
            ("22/04/2025", 1),
            ("23/04/2025", 1),
            ("24/04/2025", 1),
            ("25/04/2025", 1),
            ("05/05/2025", 1),
            ("06/05/2025", 1),
            ("07/05/2025", 1),
            ("08/05/2025", 1),
            ("09/05/2025", 1),
            ("26/05/2025", 1),
            ("27/05/2025", 1),
            ("28/05/2025", 1),
            ("29/05/2025", 1),
            ("30/05/2025", 1),
            ("25/08/2025", 1),
            ("26/08/2025", 1),
            ("27/08/2025", 1),
            ("28/08/2025", 1),
            ("29/08/2025", 1),
        ]

        for refuseDate in refuse_dates:

            collection_date = (
                datetime.strptime(refuseDate, "%d/%m/%Y") + timedelta(days=offset_days)
            ).strftime("%d/%m/%Y")

            holiday_offset = next(
                (value for date, value in bank_holidays if date == collection_date), 0
            )

            if holiday_offset > 0:
                collection_date = (
                    datetime.strptime(collection_date, "%d/%m/%Y")
                    + timedelta(days=holiday_offset)
                ).strftime("%d/%m/%Y")

            dict_data = {
                "type": "Refuse Bin",
                "collectionDate": collection_date,
            }
            bindata["bins"].append(dict_data)

        for recyclingDate in recycling_dates:

            collection_date = (
                datetime.strptime(recyclingDate, "%d/%m/%Y")
                + timedelta(days=offset_days)
            ).strftime("%d/%m/%Y")

            holiday_offset = next(
                (value for date, value in bank_holidays if date == collection_date), 0
            )

            if holiday_offset > 0:
                collection_date = (
                    datetime.strptime(collection_date, "%d/%m/%Y")
                    + timedelta(days=holiday_offset)
                ).strftime("%d/%m/%Y")

            dict_data = {
                "type": "Recycling Bin",
                "collectionDate": collection_date,
            }
            bindata["bins"].append(dict_data)

        if garden_collection_week:
            if garden_collection == 0:
                gardenstartDate = datetime(2024, 11, 11)
            elif garden_collection == 1:
                gardenstartDate = datetime(2024, 11, 4)

            garden_dates = get_dates_every_x_days(gardenstartDate, 14, 28)

            garden_bank_holidays = [
                ("23/12/2024", 1),
                ("24/12/2024", 1),
                ("25/12/2024", 1),
                ("26/12/2024", 1),
                ("27/12/2024", 1),
                ("30/12/2024", 1),
                ("31/12/2024", 1),
                ("01/01/2025", 1),
                ("02/01/2025", 1),
                ("03/01/2025", 1),
            ]

            for gardenDate in garden_dates:

                collection_date = (
                    datetime.strptime(gardenDate, "%d/%m/%Y")
                    + timedelta(days=offset_days_garden)
                ).strftime("%d/%m/%Y")

                garden_holiday = next(
                    (
                        value
                        for date, value in garden_bank_holidays
                        if date == collection_date
                    ),
                    0,
                )

                if garden_holiday > 0:
                    continue

                holiday_offset = next(
                    (value for date, value in bank_holidays if date == collection_date),
                    0,
                )

                if holiday_offset > 0:
                    collection_date = (
                        datetime.strptime(collection_date, "%d/%m/%Y")
                        + timedelta(days=holiday_offset)
                    ).strftime("%d/%m/%Y")

                dict_data = {
                    "type": "Garden Bin",
                    "collectionDate": collection_date,
                }
                bindata["bins"].append(dict_data)

        bindata["bins"].sort(
            key=lambda x: datetime.strptime(x.get("collectionDate"), "%d/%m/%Y")
        )

        return bindata
