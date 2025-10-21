<!--
SPDX-FileCopyrightText: 2025 Ben Bonacci <ben at benbonacci dot com>

SPDX-License-Identifier: GPL-3.0-only
-->

# IPmaths

## About
IPmaths is a Python module that performs common IPv4 addressing calculations for network engineers. **Please note that this module is still under active development and some features may not be available or removed altogether.**

## Roadmap
As of the v0.1.0 release of this module, the following features are available:
- [ ] Calculate the best possible subnet mask for all the required hosts  
- [ ] Calculate all the usable host IPv4 addresses with the given subnet mask  
- [X] Check if the provided IPv4 address is valid  
- [X] Check if the provided subnet mask (in CIDR) is valid  
- [ ] Check if the provided subnet mask (in decimal) is valid  
- [X] Determine if the provided subnet mask is in CIDR or decimal form  
- [ ] Convert the provided subnet mask from CIDR to decimal form  
- [ ] Convert the provided subnet mask from decimal to CIDR form  
- [ ] An education mode that explains how to perform these calculations manually  

A v1.0.0 release is expected once all the following criteria has been met.

## How it works
_This section will be completed once IPmaths reaches the v1.0.0 release._

## Install
IPmaths is listed on the Python Package Index and can be download via Python's package manager, pip.

> ```pip install ipmaths```

Then, the module can be imported into the desired Python script.

> ```import ipmaths```

Alternatively, the module can be packaged and installed manually. Please consult Python's documentation for such instructions.
