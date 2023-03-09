import asyncio
import logging
import sys
from alphaess.alphaess import alphaess
from datetime import date, timedelta

if len(sys.argv) != 4:
    appID = input("AppID: ")
    appSecret = input("AppSecret: ")
    sysSn = input("sysSn:")
else:
    appID = sys.argv[1]
    appSecret = sys.argv[2]
    sysSn = sys.argv[3]

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def main():

    logger.debug("instantiating Alpha ESS Client")
    try:
        
        client: alphaess = alphaess(appID,appSecret)
        ESSList = await client.getESSList()
        for unit in ESSList:
            if "sysSn" in unit:
              serial = unit["sysSn"]
              print(f"Getting Last Power Data for Serial: {serial}")
              lastPower = await client.getLastPowerData(serial)
            if "ppv" in lastPower:
              ppv = lastPower["ppv"]
              print(f"Real time PPV: {ppv} W")
            print(f"Getting Yesterday's Power Data for Serial: {serial}")
            yesterdaydate = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
            yesterdayPower = await client.getOneDayPowerBySn(serial,yesterdaydate)
            datacount = len(yesterdayPower)
            print(f"Retrieved: {datacount} power records for yesterday")
            yesterdayEnergy = await client.getOneDateEnergyBySn(serial,yesterdaydate)
            if "epv" in yesterdayEnergy:
                epv = yesterdayEnergy["epv"]
                print(f"PV generation yesterday: {epv} kWh")
            
            chargingInfo = await client.getChargeConfigInfo(serial)
            if "gridCharge" in chargingInfo:
                batHighCap = chargingInfo["batHighCap"]
                gridCharge = chargingInfo["gridCharge"]
                timeChae1 = chargingInfo["timeChae1"]
                timeChae2 = chargingInfo["timeChae2"]
                timeChaf1 = chargingInfo["timeChaf1"]
                timeChaf2 = chargingInfo["timeChaf2"]
                if gridCharge:
                    print(f"Charging from grid is enabled, will disable it.")
                    gridCharge = 0
                else:
                    print(f"Charging from grid is disabled, will enable it .")
                    gridCharge = 1
                await client.updateChargeConfigInfo(serial, batHighCap, gridCharge, timeChae1, timeChae2, timeChaf1, timeChaf2)
                chargingInfo = await client.getChargeConfigInfo(serial)
                if "gridCharge" in chargingInfo:
                    batHighCap = chargingInfo["batHighCap"]
                    gridCharge = chargingInfo["gridCharge"]
                    timeChae1 = chargingInfo["timeChae1"]
                    timeChae2 = chargingInfo["timeChae2"]
                    timeChaf1 = chargingInfo["timeChaf1"]
                    timeChaf2 = chargingInfo["timeChaf2"]
                if gridCharge:
                    print(f"Charging from grid is enabled, will disable it.")
                    gridCharge = 0
                else:
                    print(f"Charging from grid is disabled, will enable it .")
                    gridCharge = 1
                await client.updateChargeConfigInfo(serial, batHighCap, gridCharge, timeChae1, timeChae2, timeChaf1, timeChaf2)

            dischargingInfo = await client.getDisChargeConfigInfo(serial)
            if "ctrDis" in dischargingInfo:
                batUseCap = dischargingInfo["batUseCap"]
                ctrDis = dischargingInfo["ctrDis"]
                timeDise1 = dischargingInfo["timeDise1"]
                timeDise2 = dischargingInfo["timeDise2"]
                timeDisf1 = dischargingInfo["timeDisf1"]
                timeDisf2 = dischargingInfo["timeDisf2"]
                if ctrDis:
                    print(f"Battery Discharge Time Control is enabled, will disable it.")
                    ctrDis = 0
                else:
                    print(f"Battery Discharge Time Control is disabled, will enable it.")
                    ctrDis = 1
                await client.updateDisChargeConfigInfo(serial, batUseCap, ctrDis, timeDise1, timeDise2, timeDisf1, timeDisf2)
                dischargingInfo = await client.getDisChargeConfigInfo(serial)
                if "ctrDis" in dischargingInfo:
                    batUseCap = dischargingInfo["batUseCap"]
                    ctrDis = dischargingInfo["ctrDis"]
                    timeDise1 = dischargingInfo["timeDise1"]
                    timeDise2 = dischargingInfo["timeDise2"]
                    timeDisf1 = dischargingInfo["timeDisf1"]
                    timeDisf2 = dischargingInfo["timeDisf2"]
                    if ctrDis:
                        print(f"Battery Discharge Time Control is enabled, will disable it.")
                        ctrDis = 0
                    else:
                        print(f"Battery Discharge Time Control is disabled, will enable it.")
                        ctrDis = 1
                await client.updateDisChargeConfigInfo(serial, batUseCap, ctrDis, timeDise1, timeDise2, timeDisf1, timeDisf2)

    except Exception as e:
        logger.error(e)

asyncio.run(main())
