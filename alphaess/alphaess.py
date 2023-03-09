from datetime import datetime, date, timedelta
import time
import aiohttp
import logging
import hashlib

logger = logging.getLogger(__name__)

from voluptuous import Optional

BASEURL = "https://openapi.alphaess.com/api"

class alphaess:
    """Class for Alpha ESS."""

    def __init__(self,appID,appSecret) -> None:
        """Initialize."""
        self.appID = appID
        self.appSecret = appSecret
        self.accesstoken = None
        self.expiresin = None
        self.tokencreatetime = None
        self.refreshtoken = None

    def __headers(self):
        timestamp = str(int(time.time()))
        return {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "timestamp": f"{timestamp}",
            "sign": f"{str(hashlib.sha512((str(self.appID) + str(self.appSecret) + str(timestamp)).encode('ascii')).hexdigest())}",
            "appId": self.appID,
            "timeStamp": timestamp
        }

    async def getESSList(self) -> Optional(list):
        """According to SN to get system list data"""
        resource = f"{BASEURL}/getEssList"

        logger.debug(f"Trying to get list of registered ESS systems")

        data = await self.__get_data(resource)

        if data is not None:
            return data
        else:
            return None

    async def getLastPowerData(self,sysSn) -> Optional(list):
        """According SN to get real-time power data"""
        resource = f"{BASEURL}/getLastPowerData?sysSn={sysSn}"

        logger.debug(f"Trying to get real time power information for system {sysSn}")

        data = await self.__get_data(resource)

        if data is not None:
            return data
        else:
            return None


    async def getOneDayPowerBySn(self,sysSn,queryDate) -> Optional(list):
        """According SN to get system power data"""
        resource = f"{BASEURL}/getOneDayPowerBySn?sysSn={sysSn}&queryDate={queryDate}"

        logger.debug(f"Trying to get one day power information for system {sysSn}")

        data = await self.__get_data(resource)

        if data is not None:
            return data
        else:
            return None
    
    async def getOneDateEnergyBySn(self,sysSn,queryDate) -> Optional(list):
        """According SN to get System Energy Data"""
        resource = f"{BASEURL}/getOneDateEnergyBySn?sysSn={sysSn}&queryDate={queryDate}"

        logger.debug(f"Trying to get one day energy information for system {sysSn}")

        data = await self.__get_data(resource)

        if data is not None:
            return data
        else:
            return None

    async def getChargeConfigInfo(self,sysSn) -> Optional(list):
        """According SN to get charging setting information"""
        resource = f"{BASEURL}/getChargeConfigInfo?sysSn={sysSn}"

        logger.debug(f"Trying to get charging information for system {sysSn}")

        data = await self.__get_data(resource)

        if data is not None:
            return data
        else:
            return None

    async def getDisChargeConfigInfo(self,sysSn) -> Optional(list):
        """According to SN discharge setting information"""
        resource = f"{BASEURL}/getDisChargeConfigInfo?sysSn={sysSn}"

        logger.debug(f"Trying to get discharging information for system {sysSn}")

        data = await self.__get_data(resource)

        if data is not None:
            return data
        else:
            return None

    async def updateChargeConfigInfo(self,sysSn,batHighCap,gridCharge,timeChae1,timeChae2,timeChaf1,timeChaf2) -> Optional(dict):
        """According SN to Set charging information"""

        resource = f"{BASEURL}/updateChargeConfigInfo" 
        
        settings = {
            "sysSn": sysSn,
            "batHighCap": batHighCap,
            "gridCharge": gridCharge,
            "timeChae1": timeChae1,
            "timeChae2": timeChae2,
            "timeChaf1": timeChaf1,
            "timeChaf2": timeChaf2       
            }

        logger.debug(f"Trying to set charging information for system {sysSn}")

        data = await self.__post_data(resource,settings)

        if data is not None:
            return data
        else:
            return None

    async def updateDisChargeConfigInfo(self,sysSn,batUseCap,ctrDis,timeDise1,timeDise2,timeDisf1,timeDisf2) -> Optional(dict):
        """According SN to Set discharge information"""

        resource = f"{BASEURL}/updateDisChargeConfigInfo" 

        settings = {
            "sysSn": sysSn,
            "batUseCap": batUseCap,
            "ctrDis": ctrDis,
            "timeDise1": timeDise1,
            "timeDise2": timeDise2,
            "timeDisf1": timeDisf1,
            "timeDisf2": timeDisf2       
            }

        logger.debug(f"Trying to set discharging information for system {sysSn}")

        data = await self.__post_data(resource,settings)

        if data is not None:
            return data
        else:
            return None
 

    async def __get_data(self, path, json={}) -> Optional(list):
        """Retrieve ESS list by serial number from Alpha ESS"""

        try:
            headers = self.__headers()

            async with aiohttp.ClientSession(raise_for_status=True,trust_env=True) as session:              
                response = await session.get(
                    path,
                    headers=headers,
                    json = json
                )

                if response.status == 200:
                    json_response = await response.json()

                if "msg" in json_response and json_response["msg"] == "Success":
                    if json_response["data"] is not None:
                        return json_response["data"]
                    else:
                        return None
                
        except Exception as e:
            logger.error(e)
            raise

    async def __post_data(self, path, json) -> Optional(dict):
        """Post data to Alpha ESS"""
        try:

            headers = self.__headers()

            async with aiohttp.ClientSession(raise_for_status=True,trust_env=True) as session:
                response = await session.post(
                    path,
                    headers=headers,
                    json = json
                )

                if response.status == 200:
                    json_response = await response.json()

                if "msg" in json_response and json_response["msg"] == "Success":
                    if json_response["data"] is not None:
                        return json_response["data"]
                    else:
                        return None
                
        except Exception as e:
            logger.error(e)
            raise

    # async def __daily_statistics(self, serial):
    #     """Get daily energy statistics"""

    #     todaydate = date.today().strftime("%Y-%m-%d")

    #     logger.debug("Trying to retrieve daily statistics for serial %s, date %s", serial, todaydate)
    #     return await self.__get_data(path=f"Power/SticsByPeriod?beginDay={todaydate}&endDay={todaydate}&tDay={todaydate}&isOEM=0&SN={serial}&userID=&noLoading=true")

    # async def __system_statistics(self, serial):
    #     """Get system statistics"""

    #     todaydate = date.today().strftime("%Y-%m-%d")
    #     json = {
    #         "sn": serial,
    #         "userId": "",
    #         "statisticBy": "month",
    #         "sDate": datetime.today().replace(day=1).strftime("%Y-%m-%d"),
    #         "isOEM": 0
    #     }

    #     logger.debug("Trying to retrieve system statistics for serial %s, date %s", serial, todaydate)
    #     return await self.__post_data(path="Statistic/SystemStatistic", json=json)

    # async def __powerdata(self, serial):
    #     """Get power data"""

    #     logger.debug("Trying to retrieve power data for serial %s", serial)
    #     return await self.__get_data(path=f"ESS/GetLastPowerDataBySN?noLoading=true&sys_sn={serial}")

    # async def __settings(self, systemid):
    #     """Retrieve ESS custom settings by serial number from Alpha ESS"""

    #     logger.debug("Trying to retrieve settings for system %s,", systemid)
    #     return await self.__get_data(path=f"Account/GetCustomUseESSSetting?system_id={systemid}")

    # async def __system_id_for_sn(self, serial):
    #     """Retrieve ESS system_id for the sys_sn from Alpha ESS"""

    #     try:
    #         logger.debug(f"Getting System Id for Alpha ESS unit {serial}")
    #         systems = await self.__get_data(path="Account/GetCustomUseESSList")

    #         system = list(filter(lambda x: x["sys_sn"] == serial, systems))

    #         if system:
    #             if "system_id" in system[0]:
    #                 return system[0]["system_id"]

    #     except Exception as e:
    #         logger.error(e)
    #         raise


    # async def setbatterydischarge(self, serial, enabled, dp1start, dp1end, dp2start, dp2end, dischargecutoffsoc):
    #     """Set battery discharging"""

    #     system = await self.__system_id_for_sn(serial)

    #     settings = await self.__settings(system)
    #     settings["ctr_dis"] = int(enabled)
    #     settings["time_disf1a"] = dp1start
    #     settings["time_dise1a"] = dp1end
    #     settings["time_disf2a"] = dp2start
    #     settings["time_dise2a"] = dp2end
    #     settings["bat_use_cap"] = int(dischargecutoffsoc)
    #     settings["system_id"] = system

    #     logger.debug(f"Trying to set system settings for system {system}")
    #     await self.__post_data(path="Account/CustomUseESSSetting", json=settings)
