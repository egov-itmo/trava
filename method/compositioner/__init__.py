# pylint: disable=wrong-import-position
"""
Compositioner module helps to create optimal plants compositions taking into an account their
cohabitations and possible limitation factors
"""

__all__ = [
    "get_compositions",
    "Compatability",
    "GeneraCohabitation",
    "GlobalTerritory",
    "Plant",
    "Territory",
    "enumerations",
    "CohabitationType",
    "get_territory",
]

import os

if "USE_PYGEOS" not in os.environ:
    os.environ["USE_PYGEOS"] = "0"  # remove this if some Shapely 2.0 incompatibility is found

from compositioner.composition import get_compositions
from compositioner.models import Compatability, GeneraCohabitation, GlobalTerritory, Plant, Territory, enumerations
from compositioner.models.cohabitation import CohabitationType
from compositioner.territories import get_territory
