"""Defines the Battle.net Regions

Classes:
    Region: class to hold region identifiers

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: 2025-10-16
"""

__version__ = '1.0.0'
__author__ = 'David \'Gahd\' Couples'


class Region:

    VALID_REGIONS = ('us', 'kr', 'eu', 'tw', 'cn')

    NORTH_AMERICA = "us"
    KOREA = "kr"
    EUROPE = "eu"
    TAIWAN = "tw"
    CHINA = "cn"
    APAC = ("kr", "tw")

    class Id:

        NORTH_AMERICA = 1
        KOREA = 2
        EUROPE = 3
        TAIWAN = 4
        CHINA = 5
        APAC = (2, 4)
