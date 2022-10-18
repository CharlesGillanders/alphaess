## alphaess
This Python library logs in to cloud.alphaess.com and retrieves data on your Alpha ESS inverter, photovoltaic panels, and battery if you have one.

## Usage

Create a new Alpha ESS instance, log in, retrieve a list of Alpha ESS systems and request energy statistics of one of those Alpha ESS systems. 

## API

Currently this package uses an API that I reverse engineered the API from the Alpha ESS web app. This is an internal API subject to change at any time by Alpha ESS.

# Methods

`authenticate(username, password)` - attempts to authenticate to the ALpha ESS API with a username and password combination, returns True or False depending on successful authentication or not

The remaining methods require authentication. Will throw Exceptions on failure.

`getunits()` - get a list of ESS units in account

`getdailystatistics(serial)` - retrieves daily statistics for supplied ESS serial number

`getsystemstatistics(serial)` - retrieves system statistics for supplied ESS serial number

`getpowerdata(serial)` - retrieves current power statistics (PV output, load, grid import/export etc.) for supplied ESS serial number

`getsettings(serial)` - retrieves supplied ESS serial number settings

`getdata()` - iterate through all available Alpha ESS systems and get all statistical energy data - will return None if there are issues retrieving data from the Alpha ESS API.

`setbatterycharge(serial, enabled, cp1start, cp1end, cp2start, cp2end, chargestopsoc)` - set battery grid charging settings for the SN.

`setbatterydischarge(serial, enabled, dp1start, dp1end, dp2start, dp2end, dischargecutoffsoc)` - set battery discharge settings for the SN.
