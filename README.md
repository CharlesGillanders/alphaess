## alphaess
This Python library logs in to www.alphaess.com and retrieves data on your Alpha ESS inverter, photovoltaic panels, and battery if you have one.

## Usage

Create a new Alpha ESS instance, log in, retrieve a list of Alpha ESS systems and request energy statistics of one of those Alpha ESS systems. 

## API

Currently this package uses an API that I reverse engineered the API from the Alpha ESS web app. This is an internal API subject to change at any time by Alpha ESS.

# Methods

There are two public methods in this module

authenticate(username, password) - attempts to authenticate to the ALpha ESS API with a username and password combination, returns True or False depending on sucessful authentication or not

getdata() - having succesfully authenticated attempts to get statistical energy data on all registered Alpha ESS systems - will return None if there are issues retrieving data from the Alpha ESS API.

