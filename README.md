# sahkon-hinta

A simple CLI tool to fetch the current electricity price in Finland, using the data from [sahko.tk](https://sahko.tk/).

The program uses [Playwright](https://playwright.dev/python/) to spin up a headless browser and fetch the data from the website. The data is then parsed and printed to the console in a nice format.

Done as a part of a Cloud Services course at the Oulu University of Applied Sciences.

This was a fun learning experience, as I had never used Playwright before nor published a package to PyPI.

## Installation
Just install the package from PyPI:
```bash
python3 -m pip install sahkon-hinta
```

## Example output
```console
$ sahkon-hinta
>                 Sähkön hinta (snt/kWh) 24% alv
> Nyt   Päivän alin  Päivän ylin  7pv keskihinta  28pv keskihinta
> 6.96     5.27         11.76          5.80            6.46
>                         Lähde: sahko.tk
```
