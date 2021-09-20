import logging
import asyncio
from os import stat
import sys
import json


from alphaess.alphaess import alphaess


username = sys.argv[1]
password = sys.argv[2]



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
        statistics = await client.getdata()
        print(f"all statistics: {statistics}")


asyncio.run(main())
