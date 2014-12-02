# phlAddrParse 1.0
============
##First Line Address Parser and Standardizer
============
Will work on any US based first line address but standardizations are tweaked specifically for Philadelphia addresses.

Does not handle City, State, ZIPCode

Application currently run self contained in one directory.  See **phlAddrParse.cfg** for input and output settings.

Program attempts to adhere to USPS Pub. 28 address standards.

There are 6 files that determine most of the standardizations.   You can modify to meet your needs:

- apt.csv - postal unit designators/apt, expects a number/unit identifier to follow
- apte.csv - postal unit designator/apt, no following number/unit identifier required.
- directional.csv - pre and post directionals for addresses
- suffix.csv - usps suffixes
- saint.csv - list of Saints to help with standardizations of 'ST'
- std.csv - street name standardizations.

GIVEN:

**123R-27 north ben Franklin blv apt 2b and s pine av**

RETURNS:

**O,123,127,123R,127R,N,BENJAMIN FRANKLIN,BLVD,,APT 2B,S,PINE,AVE,,**

WHERE

|FIELD|EXAMPLE|DESCRIPTION|
| ------------- |-------------|-----|
|oeb|O| address number/range, Odd, Even, Both|
|alow|123| address number low|
|ahigh|127| address number high|
|astrlow|123R| address number low as a string|
|astrhigh|127R| address number high as a string|
|predir|N| pre directional|
|streetname|BENJAMIN FRANKLIN| street name|
|suffix|BLVD| suffix|
|postdir| | post directional|
|unit|APT 2B| unit designator/apt|
|predir2|S| pre directional for intersections, blank otherwise|
|streetname2|PINE| streetname for intersections, blank otherwise |
|suffix2|AVE| suffix for intersections, blank otherwise|
|postdir2| | post directional for intersections, blank otherwise|
|unit2| | unit designator for intersections, blank otherwise|

USAGE:

Copy `phlParseAddr` directory to same location as your Python script.

    from phlAddrParse.phlAddrParse import Parser

    parser = Parser()
    parsed = parser.parse('1234 MARKET ST')

    print parsed.streetname