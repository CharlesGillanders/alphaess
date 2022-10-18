from datetime import datetime, date, timedelta
import time
import aiohttp
import logging
import hashlib

logger = logging.getLogger(__name__)

from voluptuous import Optional

BASEURL = "https://cloud.alphaess.com/api"
AUTHPREFIX = "al8e4s"
AUTHCONSTANT = "LSZYDA95JVFQKV7PQNODZRDZIS4EDS0EED8BCWSS"
AUTHSUFFIX = "ui893ed"

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
        self.refreshtoken = None
        self.esslist = None

    def __headers(self):
        timestamp = str(int(time.time()))
        return {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "authtimestamp": f"{timestamp}",
            "authsignature": f"{AUTHPREFIX}{str(hashlib.sha512((AUTHCONSTANT + str(timestamp)).encode('ascii')).hexdigest())}{AUTHSUFFIX}"
        }

    async def authenticate(self, username, password) -> bool:
        """Authenticate."""

        resource = f"{BASEURL}/Account/Login"

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                headers = self.__headers()
                response = await session.post(
                    resource,
                    json={
                        "username": username,
                        "password": password
                    },
                    headers=headers
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
                    if "RefreshTokenKey" in json_response["data"]:
                        self.refreshtoken = json_response["data"]["RefreshTokenKey"]
                    self.tokencreatetime = datetime.utcnow()
                    self.username = username
                    self.password = password
                    logger.debug("Successfully Authenticated to Alpha ESS")
                    logger.debug("Received access token: %s", self.accesstoken)
                    return True
            except (aiohttp.ClientConnectionError) as e:
                self.__clearconnection()
                logger.error(e)
                raise

            except (aiohttp.client_exceptions.ClientConnectorError) as e:
                self.__clearconnection()
                logger.error(e)
                raise

    async def __refresh(self,) -> bool:
        """Refresh."""

        resource = f"{BASEURL}/Account/RefreshToken"

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                response = await session.post(
                    resource,
                    json={
                        "username": self.username,
                        "accesstoken": self.accesstoken,
                        "refreshtokenkey": self.refreshtoken
                    },
                    headers=self.__headers()
                )
                if response.status == 200:
                    json_response = await response.json()
                    if "info" in json_response and json_response["info"] != "Success":
                        raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status, message=json_response["info"])
                    if "AccessToken" in json_response["data"]:
                        self.accesstoken = json_response["data"]["AccessToken"]
                    if "ExpiresIn" in json_response["data"]:
                        self.expiresin = json_response["data"]["ExpiresIn"]
                    if "RefreshTokenKey" in json_response["data"]:
                        self.refreshtoken = json_response["data"]["RefreshTokenKey"]
                    self.tokencreatetime = datetime.utcnow()
                    logger.debug("Successfully refreshed access token")
                    logger.debug("Received access token: %s", self.accesstoken)
                    return True
            except (aiohttp.ClientConnectionError) as e:
                self.__clearconnection()
                logger.error(e)
                raise

            except (aiohttp.client_exceptions.ClientConnectorError) as e:
                self.__clearconnection()
                logger.error(e)
                raise

    def __clearconnection(self):
        self.accesstoken = None
        self.tokencreatetime = None
        self.expiresin = None
        self.refreshtoken = None

    async def __connection_check(self) -> bool:
        """Check if API needs re-authentication."""

        if (self.accesstoken is not None) and (self.tokencreatetime is not None) and (self.expiresin is not None) and (self.refreshtoken is not None):
            if datetime.utcnow() < (self.tokencreatetime + timedelta(seconds=(self.expiresin - 60))):
                logger.debug("API authentication token remains valid")
                return True
            else:
                return await self.__refresh()
        return await self.authenticate(self.username, self.password)

    async def getunits(self) -> Optional(list):
        """Retrieve a list of ESS units in account"""

        try:
            if self.esslist is None:
                logger.debug("Getting ESS List")
                self.esslist = await self.__get_data("Account/GetCustomMenuESSList")
            return self.esslist
        except Exception as e:
            logger.error(e)
            raise

    async def getdailystatistics(self, serial) -> Optional(list):
        """Retrieve daily statistics for supplied unit serial"""

        try:
            return await self.__daily_statistics(serial)
        except Exception as e:
            logger.error(e)
            raise

    async def getsystemstatistics(self, serial) -> Optional(list):
        """Retrieve system statistics for supplied unit serial"""

        try:
            return await self.__system_statistics(serial)
        except Exception as e:
            logger.error(e)
            raise

    async def getpowerdata(self, serial) -> Optional(list):
        """Retrieve power data for supplied unit serial"""

        try:
            return await self.__powerdata(serial)
        except Exception as e:
            logger.error(e)
            raise

    async def getsettings(self, serial) -> Optional(list):
        """Retrieve settings for supplied unit serial"""

        try:
            system = await self.__system_id_for_sn(serial)
            return await self.__settings(system)
        except Exception as e:
            logger.error(e)
            raise

    async def getdata(self) -> Optional(list):
        """Retrieve ESS list by serial number from Alpha ESS"""

        try:
            alldata = []           
            units = await self.getunits()

            for unit in units:
                if "sys_sn" in unit:
                    serial = unit["sys_sn"]
                    logger.debug(f"Retreiving energy statistics for Alpha ESS unit {serial}")
                    unit['statistics'] = await self.__daily_statistics(serial)
                    unit['system_statistics'] = await self.__system_statistics(serial)
                    unit['powerdata'] = await self.__powerdata(serial)
                    system = await self.__system_id_for_sn(serial)
                    unit['settings'] = await self.__settings(system)
                    alldata.append(unit)
            return alldata

        except Exception as e:
            logger.error(e)
            raise

    async def __get_data(self, path) -> Optional(list):
        """Retrieve ESS list by serial number from Alpha ESS"""

        if not await self.__connection_check():
            return None

        resource = f"{BASEURL}/{path}"

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                timestamp = str(int(time.time()))
                session.headers.update({'Authorization': f'Bearer {self.accesstoken}'})
                session.headers.update({'authtimestamp': f'{timestamp}'})
                session.headers.update({'authsignature': f'{AUTHPREFIX}{str(hashlib.sha512((AUTHCONSTANT + str(timestamp)).encode("ascii")).hexdigest())}{AUTHSUFFIX}'})
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

    async def __post_data(self, path, json) -> Optional(dict):
        """Request data from Alpha ESS"""
        if not await self.__connection_check():
            return None

        resource = f"{BASEURL}/{path}"

        try:
            async with aiohttp.ClientSession(raise_for_status=True) as session:
                timestamp = str(int(time.time()))
                session.headers.update({'Authorization': f'Bearer {self.accesstoken}'})
                session.headers.update({'authtimestamp': f'{timestamp}'})
                session.headers.update({'authsignature': f'{AUTHPREFIX}{str(hashlib.sha512((AUTHCONSTANT + str(timestamp)).encode("ascii")).hexdigest())}{AUTHSUFFIX}'})

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
        return await self.__post_data(path="Power/SticsByPeriod", json=json)

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
        return await self.__post_data(path="Statistic/SystemStatistic", json=json)

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
        return await self.__post_data(path=f"ESS/GetLastPowerDataBySN?noLoading=true&sys_sn={serial}", json=json)

    async def __settings(self, systemid):
        """Retrieve ESS custom settings by serial number from Alpha ESS"""

        logger.debug("Trying to retrieve settings for system %s,", systemid)
        return await self.__get_data(path=f"Account/GetCustomUseESSSetting?system_id={systemid}")

    async def __system_id_for_sn(self, serial):
        """Retrieve ESS system_id for the sys_sn from Alpha ESS"""

        try:
            logger.debug(f"Getting System Id for Alpha ESS unit {serial}")
            systems = await self.__get_data(path="Account/GetCustomUseESSList")

            system = list(filter(lambda x: x["sys_sn"] == serial, systems))

            if system:
                if "system_id" in system[0]:
                    return system[0]["system_id"]

        except Exception as e:
            logger.error(e)
            raise

    async def setbatterycharge(self, serial, enabled, cp1start, cp1end, cp2start, cp2end, chargestopsoc):
        """Set battery grid charging"""

        system = await self.__system_id_for_sn(serial)

        settings = await self.__settings(system)
        settings["grid_charge"] = int(enabled)
        settings["time_chaf1a"] = cp1start
        settings["time_chae1a"] = cp1end
        settings["time_chaf2a"] = cp2start
        settings["time_chae2a"] = cp2end
        settings["bat_high_cap"] = int(chargestopsoc)

        logger.debug(f"Trying to set system settings for system {system}")
        await self.__post_data(path="Account/CustomUseESSSetting", json=settings)

    async def setbatterydischarge(self, serial, enabled, dp1start, dp1end, dp2start, dp2end, dischargecutoffsoc):
        """Set battery discharging"""

        system = await self.__system_id_for_sn(serial)

        settings = await self.__settings(system)
        settings["ctr_dis"] = int(enabled)
        settings["time_disf1a"] = dp1start
        settings["time_dise1a"] = dp1end
        settings["time_disf2a"] = dp2start
        settings["time_dise2a"] = dp2end
        settings["bat_use_cap"] = int(dischargecutoffsoc)

        logger.debug(f"Trying to set system settings for system {system}")
        await self.__post_data(path="Account/CustomUseESSSetting", json=settings)
