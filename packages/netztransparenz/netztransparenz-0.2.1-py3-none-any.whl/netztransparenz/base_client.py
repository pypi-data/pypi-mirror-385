"""
Base class for all other clients. Handles login and health check.
"""

import requests
import logging
import io
import datetime as dt
import pandas as pd

from netztransparenz.constants import endpoints

log = logging.getLogger("BaseNtClient")
_ACCESS_TOKEN_URL = "https://identity.netztransparenz.de/users/connect/token"


class BaseNtClient:
    def __init__(
        self,
        client_id,
        client_pass,
        strict: bool = True,
        max_query_distance: dt.timedelta = dt.timedelta(days=365),
    ):
        """
        Creates the client and attempts to retrieve a token from the identity service.
        If retrieving the token fails this will raise an Exception.

            client_id -- your netztransparenz.de client id, usually starts with "cm_app_ntp_id"
            client_pass -- your netztransparenz.de client secret, usually starts with "ntp_"
            strict -- if True, raises Errors on not matching date parameters.
                      if False, returns empty dataframes in such cases.
                      Default=True
            max_query_distance -- The Api may return a HTTP 500 error if an explicit timeframe is too large.
                                  The client will split queries for linger timeframes than given timedelta
                                  into several smaller requests.
        """
        self._API_BASE_URL = "https://ds.netztransparenz.de/api/v1"
        self._api_date_format = "%Y-%m-%dT%H:%M:%S"
        self._csv_date_format = "%Y-%m-%d %H:%M %Z"
        self.strict = strict
        self.max_query_distance = max_query_distance

        response = requests.post(
            _ACCESS_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_pass,
            },
        )

        if response.ok:
            self.token = response.json()["access_token"]
        else:
            message = (
                f"Error retrieving token\n{response.status_code}:{response.reason}"
            )
            log.error(message)
            raise Exception(f"Login failed. {message}")

    def check_health(self):
        """
        Return the text response of the API health endpoint.
        Any Response but "OK" indicates a problem.
        """

        url = f"{self._API_BASE_URL}/health"
        response = requests.get(
            url, headers={"Authorization": "Bearer {}".format(self.token)}
        )
        return response.text

    def set_strict(self, strict: bool) -> None:
        """
        Set the behaviour of the client in case of bad date parameters.

            strict -- True for raising errors, False for returning empty dataframes.
        """
        self.strict = strict

    def set_max_query_distance(self, max_query_distance: dt.timedelta):
        """
        Set the maximum time that is queried with a single api call.

            strict -- True for raising errors, False for returning empty dataframes.
        """
        self.max_query_distance = max_query_distance

    def _check_preconditions(
        self,
        start: dt.datetime | None,
        start_of_data: dt.datetime,
        end: dt.datetime | None,
    ) -> bool:
        """
        Checks if both dates or none are set, if start is before end and if data can exist between start and end.
        If self.strict is True this will raise a ValueError if any check fails. Otherwise failed checks cause this function to return False.
        """
        if start is None and end is None:
            return True
        elif (start is None) or (end is None):
            if self.strict:
                raise ValueError("Start and End have to be provided both or not at all")
            return False
        elif start.astimezone(dt.UTC) > end.astimezone(dt.UTC):
            if self.strict:
                raise ValueError("End date is before the start date")
            return False
        elif start_of_data.astimezone(dt.UTC) > end.astimezone(dt.UTC):
            if self.strict:
                raise ValueError("There is no Data for the selected date range")
            return False
        return True

    def _return_empty_frame(self, endpoint: str, transformed: bool):
        if transformed:
            return pd.read_csv(
                io.StringIO(endpoints[endpoint]["transformed_header"]), sep=";"
            )
        else:
            return pd.read_csv(io.StringIO(endpoints[endpoint]["header"]), sep=";")

    def _split_timeframe(
        self, dt_begin: dt.datetime, dt_end: dt.datetime
    ) -> list[tuple[dt.datetime, dt.datetime]]:
        current_start = dt_begin
        current_end = dt_begin + self.max_query_distance
        result = []
        while current_end < dt_end:
            result.append((current_start, current_end))
            current_start = current_end
            current_end = current_start + self.max_query_distance
        result.append((current_start, dt_end))
        return result
