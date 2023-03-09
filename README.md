## alphaess
This Python library uses the Alpha ESS Open API to retrieve data on your Alpha ESS inverter, photovoltaic panels, and battery if you have one.

## Usage

Create a new Alpha ESS instance, log in, retrieve a list of Alpha ESS systems and request energy statistics of one of those Alpha ESS systems. 

## API

Currently this package uses the beta of the Open API from AlphaESS information on that API is available at https://github.com/alphaess-developer/alphacloud_open_api

### Note

To be good internet citizens, it is advised that your polling frequency for any AlphaCloud endpoints are 10 seconds at a minimum.

# Methods

There are public methods in this module that duplicate the AlphaESS OpenAPI and provide wrappers for

https://openapi.alphaess.com/api/getEssList
https://openapi.alphaess.com/api/getLastPowerData
https://openapi.alphaess.com/api/getOneDayPowerBySn
https://openapi.alphaess.com/api/getOneDateEnergyBySn 
https://openapi.alphaess.com/api/getChargeConfigInfo
https://openapi.alphaess.com/api/updateChargeConfigInfo
https://openapi.alphaess.com/api/getDisChargeConfigInfo
https://openapi.alphaess.com/api/updateDisChargeConfigInfo

There is also a method intended for use by my Home Assistant integration [https://github.com/CharlesGillanders/homeassistant-alphaESS]
`getdata()` - Attempts to get a collection of data on all registered Alpha ESS systems - will return None if there are issues retrieving data from the Alpha ESS API.
