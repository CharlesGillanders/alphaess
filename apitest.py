import logging
import asyncio
from os import stat
import sys
import datetime


from alphaess.alphaess import alphaess


username = input("username: ")
password = input("password: ")



logger = logging.getLogger('')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def main():

    logger.debug("instantiating Alpha ESS Client")

    client: alphaess = alphaess()

    logger.debug("Checking authentication")
    authenticated = await client.authenticate(username, password)

    if authenticated:
        data = await client.getdata()
        print(f"all data: {data}")
        discharge = data[0]["system_statistics"]["EDischarge"]
        charge = data[0]["system_statistics"]["ECharge"]
        index = int(datetime.date.today().strftime("%d")) - 1
        print(f"discharge: {discharge[index]}")
        print(f"charge: {charge[index]}")



asyncio.run(main())
