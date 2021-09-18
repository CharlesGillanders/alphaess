## alphaess
This Python library logs in to www.alphaess.com and retrieves data on your Alpha ESS inverter, photovoltaic panels, and battery if you have one.

## Usage

Create a new Alpha ESS instance, log in, retrieve a list of Alpha ESS systems and request details of these Alpha ESS systems. An example can be found in [alphaess/\_\_main\_\_.py](alphaess/__main__.py), and can be run using `python -m alphaess`.

## API

Currently this package uses an API that I reverse engineered the API from the Alpha ESS web app. This is an internal API subject to change at any time by Alpha ESS.


## Getting started

Run the following commands to set up a new virtualenv and run the alphaess API example:

    git clone https://github.com/CharlesGillanders/alphaess
    cd alphaess
    python3 -m venv venv                    # create a new virtual environment in the directory 'venv'
    . venv/bin/activate                     # activate this environment
    ./setup.py install                      # install all dependencies
    python -m alphaess 'username' 'password' # retrieve data for today

After setting up like this, you can just run the python from the virtualenv each time you want to run it:

    venv/bin/python -m alphaess 'username' 'password'

If you want to create your own client, start from alphaess/\_\_main\_\_.py. Copy it and change it to your liking, and then run it like this:

    venv/bin/python myscript.py 'username' 'password'
