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
            data = await client.getdata()
            print(f"all data: {data}")
            if data:
                if "sys_sn" in data[0]:
                    serial = data[0]['sys_sn']
            print(f"serial: {serial}")

            index = int(datetime.date.today().strftime("%d")) - 1
            if "EDischarge" in data:
                discharge = data[0]["system_statistics"]["EDischarge"]
                print(f"discharge: {discharge[index]}")
            if "ECharge" in data:
                charge = data[0]["system_statistics"]["ECharge"]        
                print(f"charge: {charge[index]}")

            await client.setbatterycharge(serial, False, "00:00", "00:00", "00:00", "00:00", 100)
            await client.setbatterydischarge(serial, True, "08:00", "23:00", "00:00", "00:00", 15)

    except aiohttp.ClientResponseError as e:
        if e.status == 401:
            logger.error("Authentication Error")
        else:
            logger.error(e)
    except Exception as e:
        logger.error(e)

asyncio.run(main())
