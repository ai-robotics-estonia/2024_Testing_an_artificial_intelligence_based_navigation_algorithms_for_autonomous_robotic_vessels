# Navigation
## Getting started

Install requirements:

    pip install -r requirements.txt

Run the runner:

    py runner.py

## Project structure

map_reader - submodule that helps to retrieve map in a matrix format

colreg3.py - module to run animation of ship moving on the following map
implementing basic COLREG rules with Artificial Potential Field

occupancy_map_translator - lists integers as obstacle types. 
Currently - 1: 'ship', 2: 'nonmoving' (usually land), 3: 'green buoy', 4: 'red buoy'.
 Can be edited, for example, if there is a need to simulate obstacles in addition to the non-moving 
land, for example other ships.