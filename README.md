curb-geocoder
==================

A tool to build reference data for a curbside ArcGIS geocoder

## Overview

A typical geocoder will return the location of an address by interpolating along a street centerline. A curb geocoder enhances this process by locating to the curb line of a specific parcel. This provides more accurate results and is useful for locating street-adjacent assets such as streetlights, fire hydrants, and trees. As an alternative to curbs, you can also supply building footprints to estimate front door of a building.

In the graphic below, the red points show where the geocoder will locate to when searching for a given address (green points).

![Curb Geocoder](http://i.imgur.com/q47ewKb.png)



This project contains a Python script to process and output the reference data for an ArcGIS address locator. Just plug in your data and let the script take care of the rest.

## Installation

The script is designed to run against the 64-bit Python install for ArcGIS (more on that [here](http://resources.arcgis.com/en/help/main/10.1/index.html#/Background_Geoprocessing_64_bit/002100000040000000/)). It should work on the standard 32-bit version as well.

You will a need file geodatabase with the following data, placed directly into the repo:

- street centerlines
- curb polygons (or building footprints)
- address points (generally parcel centroids) with a field for the intersecting poly ID (do this first using a spatial join)

The only dependency not included is the Shapely library. You can find a Windows installer of that [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/). Make sure to get the version that matches the bits of your Python install, not the OS.

## Configuration

The project includes a `sample_config.py` file with settings you'll need to source and output the data. `input` describes the names of the input layers, and takes a map of field names for the following:

### Addresses
- `address_id` is the unique ID of each address
- `address_full` is a full address string, such as `1234 W MARKET ST`
- `poly_id` is the object ID of the curb/building polygon

### Streets
- `street_name` is the name of the street
- `left_from`, '`left_to', `right_from`, and '`right_to' specify the address ranges for the street segment

`output` contains the names of the two output layers: construction lines (described below) and a directory for CSV/logging output. This directory will be created automatically if it doesn't exist.

There are several other parameters in `logging` and `debug` which may be useful if you need to develop against the script.

Once the config file is set up, save and rename the file to `config.py`.

## Execution

To run the script, open a command prompt, navigate to the project folder, and type `build_data.py`.

## Output

The script has two outputs:

- a timestamped CSV file of all curb points (in `/output`)
- a feature class of construction lines (in the geodatabase)

The construction lines connect each address point to the corresponding street segment. This can be useful for troubleshooting issues with address-centerline relationships. Longer lines indicate unreliable matches and should usually be looked into.

The `error.log` file in `/output` contains all errors and warnings from the script. Standard messages are:

- `Addr num 0`: the address number was 0 and could not be matched to a street segment
- `No poly ID`: the address had no curb polygon ID
- `No street named ___`: street name could not be found
- `Multiple exact street matches`: the address matched more than one street segment based on name and address range
- `Out of range`: no street segments with a matching address range
- `No poly with ID ___`: no curb/building poly with that object ID
- `Block poly ___ has a null vertex`: handles an issue with donut poly geometries

If any of these appear, the address was not processed and will need to be looked at individually.

## Building the Geocoder

- Add the CSV output to a map document
- Right-click the layer and select "Display XY Data..."
- Export the XY layer to a feature class
- Create a new address locator with the `US Address - Single House` style

## Feedback

Have a bug or suggestion? Go ahead and submit an issue!