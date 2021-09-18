from datetime import datetime, timedelta
import aiohttp
from async_timeout import timeout
import logging

logger = logging.getLogger(__name__)

from voluptuous import Optional

BASEURL="https://www.alphaess.com/api"

HEADER = {
    "Content-Type": "application/json",
    "Connection": "keep-alive",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "no-cache"
}

class alphaess:
    """Class for Alpha ESS."""

    def __init__(self) -> None:
        """Initialize."""
        self.username = None
        self.serial = None
        self.accesstoken = None
        self.password = None
        self.expiresin = None
        self.tokencreatetime = None


    def authenticate(self, username, password) -> bool:
        """Authenticate."""

        logger.debug("Trying authentication with username: %s  password: %s",username,password)
        with aiohttp.ClientSession() as session:
            response = session.post(
                    f"{BASEURL}/Account/Login",
                    json={
                        "username": username,
                        "password": password,
                    },
                    headers=HEADER
            )

            try:
                response.raise_for_status()
            except:
                pass

            if response.status != 200:
                return False
            json_response = response.json()

            if "info" in json_response and json_response["info"] != "Success":
                return False
            else:
                if "AccessToken" in json_response["data"]:
                    self.accesstoken = json_response["data"]["AccessToken"]
                    if "ExpiresIn" in json_response["data"]:
                        self.expiresin = json_response["data"]["ExpiresIn"]
                    if "TokenCreateTime" in json_response["data"]:
                         if "M" in json_response["data"]["TokenCreateTime"]:
                             self.tokencreatetime = datetime.strptime(json_response["data"]["TokenCreateTime"],"%m/%d/%Y %I:%M:%S %p")
                         else:
                             self.tokencreatetime =  datetime.strptime(json_response["data"]["TokenCreateTime"],"%Y-%m-%d %H:%M:%S")
                    self.username = username
                    self.password = password
                    logger.info("Successfully Authenticated to Alpha ESS")
                    logger.debug("Received access token: %s",self.accesstoken)

        return True  

    def connection_check(self) -> bool:
        """Check if API needs re-authentication."""

        if self.accesstoken is not None:
            if (self.expiresin is not None) and (self.tokencreatetime is not None):
                    timediff = datetime.utcnow() - self.tokencreatetime
                    if timediff.total_seconds() < self.expiresin:
                        logger.debug("API authentication token remains valid")
                        return True
        self.authenticate(self.username,self.password)
        return True

    def ess_list(self) -> Optional(list):
        """Retrieve ESS list by serial number from Alpha ESS"""

        if not self.connection_check():
            return None

        resource = f"{BASEURL}/Account/GetCustomMenuESSlist"

        with aiohttp.ClientSession() as session:
            session.headers.update({'Authorization': f'Bearer {self.accesstoken}'})
            response = session.get(resource)

            try:
                response.raise_for_status()
            except:
                pass
            if response.status != 200:
              return None

            json_response = response.json()

            if "info" in json_response and json_response["info"] != "Success":
                return None
            else:
                if json_response["data"] is not None:
                    return json_response["data"]
                else:
                    return None