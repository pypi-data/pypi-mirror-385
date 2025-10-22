# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import copy
import json
import time
import urllib.error as url_error
import urllib.parse as url_parse
import urllib.request as url_request
from typing import Optional

from .conduit import conduit
from .environment import USER_AGENT
from .exceptions import Error
from .logger import logger


class BMOAPIError(Error):
    """Raised when the Bugzilla API returns an error response."""

    def __init__(self, msg: Optional[str] = None):
        super().__init__(f"Bugzilla Error: {msg if msg else 'Unknown Error'}")


class BMOAPI:
    def get(self, method: str, headers: Optional[dict] = None) -> dict:
        req_args = self._build_request(method=method, headers=headers)
        logger.debug("%s %s", req_args["url"], self._sanitise_req(req_args))

        try:
            with url_request.urlopen(url_request.Request(**req_args)) as r:
                res = json.load(r)
        except (url_error.HTTPError, OSError) as err:
            raise BMOAPIError(err)
        except json.JSONDecodeError:
            raise BMOAPIError("Malformed JSON")

        if "error" in res and res["error"]:
            raise BMOAPIError(
                res.get("message", "Error #%s" % res.get("code", "Unknown error"))
            )
        return res

    @staticmethod
    def _build_request(*, method: str, headers: Optional[dict] = None) -> dict:
        """Return dict with Request args for calling the specified BMO method."""
        bmo_url = conduit.repo.bmo_url
        headers = headers or {}
        return {
            "url": url_parse.urljoin(bmo_url, "rest/%s" % method),
            "method": "GET",
            "headers": {**headers, "User-Agent": USER_AGENT},
        }

    @staticmethod
    def _sanitise_req(req_args: dict):
        sanitised = copy.deepcopy(req_args)
        if "X-PHABRICATOR-TOKEN" in sanitised.get("headers"):
            sanitised["headers"]["X-PHABRICATOR-TOKEN"] = "cli-XXXX"
        return sanitised

    def _req_with_retries(
        self, endpoint: str, headers: Optional[dict] = None, retries: int = 3
    ) -> dict:
        for attempt in range(retries):
            try:
                result = self.get(endpoint, headers)
                break
            except BMOAPIError as e:
                logger.debug(e)

            time.sleep(1.0 * attempt)
        else:
            raise BMOAPIError(f"Reached maximum retries for BMO API (/{endpoint}).")

        return result

    def whoami(self) -> dict:
        return self._req_with_retries(
            "whoami", headers={"X-PHABRICATOR-TOKEN": conduit.load_api_token()}
        )


bmo = BMOAPI()
