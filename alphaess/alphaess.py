from datetime import datetime, timedelta, date
import re
import aiohttp
from async_timeout import timeout
import logging
import json

logger = logging.getLogger(__name__)

from voluptuous import Optional

BASEURL = "https://cloud.alphaess.com/api"

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

    async def authenticate(self, username, password) -> bool:
        """Authenticate."""

        resource = f"{BASEURL}/Account/Login"

        logger.debug("Trying authentication with username: %s  password: %s", username, password)
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                response = await session.post(
                    resource,
                    json={
                        "username": username,
                        "password": password,
                    },
                    headers=HEADER
                )
                if response.status == 200:
                    json_response = await response.json()
                    if "info" in json_response and json_response["info"] != "Success":
                        if "incorrect user name or password" in json_response["info"].casefold():
                            raise aiohttp.ClientResponseError(response.request_info, response.history, status=401,
                                                              message=json_response["info"])
                        else:
                            raise aiohttp.ClientResponseError(response.request_info, response.history,
                                                              status=response.status, message=json_response["info"])
                    if "AccessToken" in json_response["data"]:
                        self.accesstoken = json_response["data"]["AccessToken"]
                    if "ExpiresIn" in json_response["data"]:
                        self.expiresin = json_response["data"]["ExpiresIn"]
                    if "TokenCreateTime" in json_response["data"]:
                        TokenCreateTime = json_response["data"]["TokenCreateTime"]
                        if "M" in json_response["data"]["TokenCreateTime"]:
                            self.tokencreatetime = datetime.strptime(TokenCreateTime,"%m/%d/%Y %I:%M:%S %p")
                        else:
                            if len(TokenCreateTime.split("/")) == 3:
                              self.tokencreatetime = datetime.strptime(TokenCreateTime,"%Y/%m/%d %H:%M:%S")
                            if len(TokenCreateTime.split("-")) == 3:
                                self.tokencreatetime = datetime.strptime(TokenCreateTime,"%Y-%m-%d %H:%M:%S")
                    self.username = username
                    self.password = password
                    logger.debug("Successfully Authenticated to Alpha ESS")
                    logger.debug("Received access token: %s", self.accesstoken)
                    return True
            except (aiohttp.ClientConnectionError) as e:
                logger.error(e)
                raise

            except (aiohttp.client_exceptions.ClientConnectorError) as e:
                logger.error(e)
                raise

    async def __connection_check(self) -> bool:
        """Check if API needs re-authentication."""

        if self.accesstoken is not None:
            if (self.expiresin is not None) and (self.tokencreatetime is not None):
                timediff = datetime.utcnow() - self.tokencreatetime
                if timediff.total_seconds() < self.expiresin:
                    logger.debug("API authentication token remains valid")
                    return True
        await self.authenticate(self.username, self.password)
        return True

    async def __ess_list(self) -> Optional(list):
        """Retrieve ESS list by serial number from Alpha ESS"""

        if not await self.__connection_check():
            return None

        resource = f"{BASEURL}/Account/GetCustomMenuESSlist"

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                session.headers.update({'Authorization': f'Bearer {self.accesstoken}'})
                response = await session.get(resource)

                if response.status == 200:
                    json_response = await response.json()

                if "info" in json_response and json_response["info"] != "Success":
                    raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status,
                                                      message=json_response["info"])

                if json_response["data"] is not None:
                    return json_response["data"]
                else:
                    return None
            except Exception as e:
                logger.error(e)
                raise

    async def getdata(self) -> Optional(list):
        """Retrieve ESS list by serial number from Alpha ESS"""

        if not await self.__connection_check():
            return None

        try:

            alldata = []
            units = await self.__ess_list()
            logger.debug(alldata)

            for unit in units:
                if "sys_sn" in unit:
                    serial = unit["sys_sn"]
                    logger.debug(f"Retreiving energy statistics for Alpha ESS unit {serial}")
                    unit['statistics'] = await self.__daily_statistics(serial)
                    unit['system_statistics'] = await self.__system_statistics(serial)
                    unit['powerdata'] = await self.__powerdata(serial)
                    alldata.append(unit)
            return alldata

        except Exception as e:
            logger.error(e)
            raise

    async def data_request(self, path, json) -> Optional(dict):
        """Request data from Alpha ESS"""
        if not await self.__connection_check():
            return None

        resource = f"{BASEURL}/{path}"

        try:
            async with aiohttp.ClientSession(raise_for_status=True) as session:
                session.headers.update({'Authorization': f'Bearer {self.accesstoken}'})
                response = await session.post(
                    resource,
                    json=json
                )

            if response.status == 200:
                json_response = await response.json()

            if "info" in json_response and json_response["info"] != "Success":
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status,
                                                  message=json_response["info"])

            if json_response["data"] is not None:
                return json_response["data"]
            else:
                logger.debug("didn't find data in response")
                return None

        except Exception as e:
            logger.error(e)
            raise

    async def __daily_statistics(self, serial):
        """Get daily energy statistics"""

        todaydate = date.today().strftime("%Y-%m-%d")
        json = {
            "beginDay": todaydate,
            "endDay": todaydate,
            "tDay": todaydate,
            "isOEM": 0,
            "SN": serial,
            "userId": "",
            "noLoading": True,
        }

        logger.debug("Trying to retrieve daily statistics for serial %s, date %s", serial, todaydate)
        return await self.data_request(path="Power/SticsByPeriod", json=json)

    async def __system_statistics(self, serial):
        """Get system statistics"""

        todaydate = date.today().strftime("%Y-%m-%d")
        json = {
            "sn": serial,
            "userId": "",
            "statisticBy": "month",
            "sDate": datetime.today().replace(day=1).strftime("%Y-%m-%d"),
            "isOEM": 0
        }

        logger.debug("Trying to retrieve system statistics for serial %s, date %s", serial, todaydate)
        return await self.data_request(path="Statistic/SystemStatistic", json=json)

    async def __powerdata(self, serial):
        """Get power data"""

        todaydate = date.today().strftime("%Y-%m-%d")
        json = {
            "SN": serial,
            "noLoading": True,
            "userId": "",
            "isOEM": 0,
            "sys_sn": serial
        }
        logger.debug("Trying to retrieve power data for serial %s, date %s", serial, todaydate)
        return await self.data_request(path=f"ESS/GetLastPowerDataBySN?noLoading=true&sys_sn={serial}", json=json)
