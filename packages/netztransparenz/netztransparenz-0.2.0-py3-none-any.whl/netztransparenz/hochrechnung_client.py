"""
Client for all /<online>hochrechnung/ and /prognose/ Endpoints
"""

from netztransparenz.base_client import BaseNtClient
from netztransparenz.constants import endpoints
import requests
import datetime as dt
import io

import pandas as pd

_csv_date_format = "%Y-%m-%d %H:%M %Z"


class HochrechnungClient(BaseNtClient):
    def _basic_read_nt(
        self,
        resource_url,
        dt_begin: dt.datetime | None = None,
        dt_end: dt.datetime | None = None,
        transform_dates=False,
    ):
        """
        Internal method to read data in one of the common formats of th nt portal.
        Target format is: Dates separated in "Datum", "von", "Zeitzone von", "bis", "Zeitzone bis".
        Return a pandas Dataframe with data of the endpoint specified with resource_url.
        If either dt_begin or dt_end is None, all available data will be queried.

            resource_url -- url of the endpoint without the base url and without leading or trailing "/"
            earliest_data -- first datapoint in the source collection
            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        if not self._check_preconditions(
            dt_begin, endpoints[f"/{resource_url}"]["first_data"], dt_end
        ):
            return self._return_empty_frame(f"/{resource_url}", transform_dates)

        url = f"{self._API_BASE_URL}/data/{resource_url}"
        if (dt_begin is not None) and (dt_end is not None):
            start_of_data = dt_begin.strftime(self._api_date_format)
            end_of_data = dt_end.strftime(self._api_date_format)
            url = f"{url}/{start_of_data}/{end_of_data}"

        response = requests.get(
            url, headers={"Authorization": "Bearer {}".format(self.token)}
        )
        response.raise_for_status()
        df = pd.read_csv(
            io.StringIO(response.text),
            sep=";",
            header=0,
            decimal=",",
            thousands=".",
            na_values=["N.A.", "N.E."],
        )

        if transform_dates:
            df["von"] = pd.to_datetime(
                df["Datum"] + " " + df["von"] + " " + df["Zeitzone von"],
                format=_csv_date_format,
                utc=True,
            )
            df["bis"] = pd.to_datetime(
                df["Datum"] + " " + df["bis"] + " " + df["Zeitzone bis"],
                format=_csv_date_format,
                utc=True,
            )
            # The end of timeframes may be 00:00 of the next day which is not correctly represented in timestamps
            df["bis"] = df["bis"].where(
                df["bis"].dt.time != dt.time(0, 0), df["bis"] + dt.timedelta(days=1)
            )
            df = df.drop(["Datum", "Zeitzone von", "Zeitzone bis"], axis=1).set_index(
                "von"
            )

        return df

    def hochrechnung_solar(
        self,
        dt_begin: dt.datetime | None = None,
        dt_end: dt.datetime | None = None,
        transform_dates=False,
    ):
        """
        Return a pandas Dataframe with data of the endpoint /hochrechnung/Solar.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        self._check_preconditions(dt_begin, dt.datetime(2011, 3, 31, 22), dt_end)
        return self._basic_read_nt(
            "hochrechnung/Solar", dt_begin, dt_end, transform_dates
        )

    def hochrechnung_wind(
        self,
        dt_begin: dt.datetime | None = None,
        dt_end: dt.datetime | None = None,
        transform_dates=False,
    ):
        """
        Return a pandas Dataframe with data of the endpoint /hochrechnung/Wind.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        self._check_preconditions(dt_begin, dt.datetime(2011, 3, 31, 22), dt_end)
        return self._basic_read_nt(
            "hochrechnung/Wind", dt_begin, dt_end, transform_dates
        )

    def online_hochrechnung_windonshore(
        self,
        dt_begin: dt.datetime | None = None,
        dt_end: dt.datetime | None = None,
        transform_dates=False,
    ):
        """
        Return a pandas Dataframe with data of the endpoint /onlineHochrechnung/Windonshore.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-12-31T23:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        self._check_preconditions(dt_begin, dt.datetime(2011, 12, 31, 23), dt_end)
        return self._basic_read_nt(
            "onlineHochrechnung/Windonshore", dt_begin, dt_end, transform_dates
        )

    def online_hochrechnung_windoffshore(
        self,
        dt_begin: dt.datetime | None = None,
        dt_end: dt.datetime | None = None,
        transform_dates=False,
    ):
        """
        Return a pandas Dataframe with data of the endpoint /onlineHochrechnung/Windoffshore.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-12-31T23:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        self._check_preconditions(dt_begin, dt.datetime(2011, 12, 31, 23), dt_end)
        return self._basic_read_nt(
            "onlineHochrechnung/Windoffshore", dt_begin, dt_end, transform_dates
        )

    def online_hochrechnung_solar(
        self,
        dt_begin: dt.datetime | None = None,
        dt_end: dt.datetime | None = None,
        transform_dates=False,
    ):
        """
        Return a pandas Dataframe with data of the endpoint /onlineHochrechnung/Solar.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-12-31T23:00:00)
            dt_end -- datetime object for end of data in UTC
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        self._check_preconditions(dt_begin, dt.datetime(2011, 12, 31, 23), dt_end)
        return self._basic_read_nt(
            "onlineHochrechnung/Solar", dt_begin, dt_end, transform_dates
        )

    def prognose_solar(
        self,
        dt_begin: dt.datetime | None = None,
        dt_end: dt.datetime | None = None,
        transform_dates=False,
    ):
        """
        Return a pandas Dataframe with data of the endpoint /prognose/Solar.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC (no values after: 2022-12-15T00:00:00)
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_nt("prognose/Solar", dt_begin, dt_end, transform_dates)

    def prognose_wind(
        self,
        dt_begin: dt.datetime | None = None,
        dt_end: dt.datetime | None = None,
        transform_dates=False,
    ):
        """
        Return a pandas Dataframe with data of the endpoint /prognose/Wind.
        If either dt_begin or dt_end is None, all available data will be queried.

            dt_begin -- datetime object for start of data in UTC (no values before: 2011-03-31T22:00:00)
            dt_end -- datetime object for end of data in UTC (no values after: 2022-12-15T00:00:00)
            transform_dates -- The data contains times with date, time and timezone in separate columns
                               if this option resolves to "True" the times will be transformed into two
                               columns "von" and "bis" that contain fully qualified timestamps. (default: False)
        """
        return self._basic_read_nt("prognose/Wind", dt_begin, dt_end, transform_dates)
