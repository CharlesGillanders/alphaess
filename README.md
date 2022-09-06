## alphaess
This Python library logs in to cloud.alphaess.com and retrieves data on your Alpha ESS inverter, photovoltaic panels, and battery if you have one.

## Usage

Create a new Alpha ESS instance, log in, retrieve a list of Alpha ESS systems and request energy statistics of one of those Alpha ESS systems. 

## API

Currently this package uses an API that I reverse engineered the API from the Alpha ESS web app. This is an internal API subject to change at any time by Alpha ESS.

# Methods

There are four public methods in this module

authenticate(username, password) - attempts to authenticate to the ALpha ESS API with a username and password combination, returns True or False depending on successful authentication or not

getdata() - having successfully authenticated attempts to get statistical energy data on all registered Alpha ESS systems - will return None if there are issues retrieving data from the Alpha ESS API.

setbatterycharge(serial, enabled, cp1start, cp1end, cp2start, cp2end, chargestopsoc) - having successfully authenticated set battery grid charging settings for the SN.

setbatterydischarge(serial, enabled, dp1start, dp1end, dp2start, dp2end, dischargecutoffsoc) - having successfully authenticated set battery discharge settings for the SN.
