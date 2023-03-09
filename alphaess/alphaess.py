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


    async def getdata(self) -> Optional(list):
        """Get All Data For All serial numbers from Alpha ESS"""

        try:
            alldata = []
            units = await self.getESSList()
            logger.debug(alldata)

            for unit in units:
                if "sysSn" in unit:
                    serial = unit["sysSn"]
                    unit['OneDayEnergy'] = await self.getOneDateEnergyBySn(serial,date.today().strftime("%Y-%m-%d"))
                    unit['RealTimePower'] = await self.getLastPowerData(serial)
                    unit['ChargeConfig'] = await self.getChargeConfigInfo(serial)
                    unit['DisChargeConfig'] = await self.getDisChargeConfigInfo(serial)
                    alldata.append(unit)
            return alldata

        except Exception as e:
            logger.error(e)
            raise