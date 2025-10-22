"""SOLARMOON CALCULATIONS.

Python Package to provide sun and moon calculations to interact with Meteocat Home Assistant Integration
SPDX-License-Identifier: Apache-2.0

For more details about this package, please refer to the documentation at
https://github.com/figorr/solarmoonpy
"""

# solarmoonpy/__init__.py
from .version import __version__
from .moon import moon_phase, moon_day, moon_rise_set, illuminated_percentage, moon_distance, moon_angular_diameter
from .location import Location, LocationInfo

__all__ = [
    "moon_phase",
    "moon_day", 
    "moon_rise_set", 
    "illuminated_percentage", 
    "moon_distance", 
    "moon_angular_diameter", 
    "Location", 
    "LocationInfo"
]
