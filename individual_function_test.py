import logging
import asyncio
import aiohttp
import sys
import datetime

from alphaess.alphaess import alphaess

if len(sys.argv) != 3:
    username = input("username: ")
    password = input("password: ")
else:
    username = sys.argv[1]
    password = sys.argv[2]

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
            # Get a list of available ESS units
            essunits = await client.getunits()

            print(f"units: {essunits}")

            # Explicitly extract serial numbers
            myunits = []
            for unit in essunits:
                if "sys_sn" in unit:
                    myunits.append(unit["sys_sn"])

            print(f"my unit serial numbers: {myunits}")

            # Get stats for each
            for serial in myunits:
                dailystatistics = await client.getdailystatistics(serial)
                print(f"daily statistics for {serial}: {dailystatistics}")

                systemstatistics = await client.getsystemstatistics(serial)
                print(f"system statistics for {serial}: {systemstatistics}")

                powerdata = await client.getpowerdata(serial)
                print(f"power data for {serial}: {powerdata}")

                settings = await client.getsettings(serial)
                print(f"settings for {serial}: {settings}")
            
    except aiohttp.ClientResponseError as e:
        if e.status == 401:
            logger.error("Authentication Error")
        else:
            logger.error(e)
    except Exception as e:
        logger.error(e)

asyncio.run(main())
