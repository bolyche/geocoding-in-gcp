import os
import json
import backoff
import requests
from pathlib import Path
from typing import Dict, Optional, Union

from utils.error_handling import client_error, print_backoff

API_TOKEN = ".."  # os.environ["API_TOKEN"]


class GeocodeIPs:
    """Rate limited Geocoding API class returning geo info per IP"""

    GEO_URL = "https://api.ipgeolocation.io/ipgeo"
    MAX_REQUEST_TIME = 300
    SAVE_FAILED_IPS = "data/ip_addresses_broken.jsonl"

    def __init__(self) -> None:
        self._request_session = requests.Session()
        self._request_session.params = {"apiKey": self._get_api_token()}
        self._request_session.headers = {
            "Content-Type": "application/json",
        }

    @staticmethod
    def _get_api_token() -> str:
        # Get token from Secret Manager or other secrets system
        # I've put the API_TOKEN on a global scope here just to make it easy to spot at the top
        return API_TOKEN

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_time=MAX_REQUEST_TIME,
        giveup=client_error,
        on_backoff=print_backoff,
    )
    def _get_request(
        self, params: Optional[Dict] = None, data: Optional[Union[Dict, str]] = None
    ) -> Optional[requests.models.Response]:
        response = self._request_session.get(url=self.GEO_URL, data=data, params=params)
        if 400 <= response.status_code < 500:
            self._handle_broken_ip(params=params, message=response.text)
            # response.raise_for_status() -> could call this here, depends on the pipeline
        else:
            return response

    def get_ip_geo_unfiltered(self, ip: str) -> Optional[Dict]:
        response = self._get_request(params={"ip": ip})
        if response:
            return json.loads(response.content)

    def _handle_broken_ip(self, params: Dict, message: Dict) -> None:
        with open(Path(os.getcwd(), self.SAVE_FAILED_IPS), "a+") as outfile:
            data = params
            data.update({"message": message})
            json.dump(data, outfile)
            outfile.write("\n")
