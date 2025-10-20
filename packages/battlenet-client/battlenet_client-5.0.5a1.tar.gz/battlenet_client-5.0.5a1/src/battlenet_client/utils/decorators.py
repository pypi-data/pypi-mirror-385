"""Defines the decorators used in this package

Functions:
   verify_region

Misc Variables:
    __version__
    __author__

Author: David "Gahd" Couples
License: GPL v3
Copyright: February 24, 2022
"""
import functools

from .exceptions import BNetGrantError, BNetRegionNotFoundError
from .constants import Region


__version__ = '1.1.0'
__author__ = 'David \'Gahd\' Couples'


def verify_region(func):
    """Verifies the function's first parameter is a valid region abbreviation

    Raises:
        BNetRegionNotFoundError: when the region (arg[0]) is not a valid region tag
    """
    @functools.wraps(func)
    def wrapper_verify_region(*args, **kwargs):
        if args[0].lower() not in Region.VALID_REGIONS:
            raise BNetRegionNotFoundError('Region not found')

        return func(*args, **kwargs)
    return wrapper_verify_region


def verify_grant_type(target_grant_type):
    """ Verfies the grant type is valid

    Args:
        target_grant_type (str): valid grant type

    Raises:
        BNetGrantError: when the grant type is not valid
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'grant_type') and self.grant_type != target_grant_type:
                raise BNetGrantError(f"Invalid grant type: {self.grant_type}")
            return func(self, *args, **kwargs)
        return wrapper

    if callable(target_grant_type):
        return decorator(target_grant_type)
    else:
        return decorator
