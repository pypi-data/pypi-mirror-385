#!/usr/bin/env python

""""""
# IPmaths - A Python module that performs common IPv4 addressing calculations for network engineers.

# SPDX-FileCopyrightText: 2025 Ben Bonacci <ben at benbonaccci dot com>
# SPDX-License-Identifier: GPL-3.0-only

""""""
import re

IP4_ADDR_REGEX = re.compile("^[0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}$")
#MASK_DECI_REGEX = re.compile("^$")
MASK_CIDR_REGEX = re.compile("^[/][1-9]{1,3}$")


## Default preferences
prefMaskFormatCIDR = False # Stub;
prefVerboseMode = False # Stub;
prefEducateMode = False # Stub;


## Functions
def calc_ip4_hosts(address: str, mask: str) -> dict:
    """Calculate all the usable host IPv4 addresses with the subnet mask"""
    pass # Stub;

def calc_subnet_mask(address: str, requiredHosts: int) -> str:
    """Calculate the best possible subnet mask for all the required hosts"""
    pass # Stub;

def check_mask_format(mask: str) -> str:
    """Check the format of the subnet mask"""
    if MASK_CIDR_REGEX.search(mask) and int(mask[1:]) <= 128:
        return "CIDR"
    elif IP4_ADDR_REGEX.search(mask):
        return "Decimal"
    else:
        return "Unknown"

def is_ip4_valid(address: str) -> bool:
    """Check if provided IPv4 address is valid"""
    if IP4_ADDR_REGEX.search(address):
        return True
    else:
        return False

def is_mask_valid(mask: str, format: str) -> bool:
    """Check if provided subnet mask is valid"""
    if format.lower() == "c":
        if MASK_CIDR_REGEX.search(mask) and int(mask[1:]) <= 128:
            return True
        else:
            return False
    elif format.lower() == "d":
        if IP4_ADDR_REGEX.search(mask):
            # Stub;
            return True
        else:
            return False
    else:
        return "Unknown"

def crvt_mask_binary(mask: str) -> str:
    """Convert the subnet mask from decimal format to binary format"""
    pass # Stub;

def crvt_mask_decimal(mask: str) -> str:
    """Convert the subnet mask from binary format to decimal format"""
    pass # Stub;



if __name__ == "__main__":
    print("IPmaths is a Python module and not an interactive Python script. Please import IPmaths in order to use it. Consult the documentation for further assistance.")
