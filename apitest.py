from distutils.log import debug
import logging
import asyncio
from urllib import response
import aiohttp
from os import stat
import sys
import datetime


from alphaess.alphaess import alphaess


username = input("username: ")
password = input("password: ")



logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def main():

    logger.debug("instantiating Alpha ESS Client")

    client: alphaess = alphaess()

    logger.debug("Checking authentication")
    try:
        authenticated = await client.authenticate(username, password)
    
        if authenticated:
            data = await client.getdata()
            print(f"all data: {data}")

            index = int(datetime.date.today().strftime("%d")) - 1
            if "EDischarge" in data:
                discharge = data[0]["system_statistics"]["EDischarge"]
                print(f"discharge: {discharge[index]}")
            if "ECharge" in data:
                charge = data[0]["system_statistics"]["ECharge"]        
                print(f"charge: {charge[index]}")

    except aiohttp.ClientResponseError as e:
        if e.status == 401:
            logger.error("Authentication Error")
        else:
            logger.error(e)
    except Exception as e:
        logger.error(e)



asyncio.run(main())
