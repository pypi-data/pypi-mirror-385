#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__copyright__ = """ This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Department of Chemistry and Applied Biosciences, Reiher Group.
See LICENSE.txt for details.
"""

from typing import List
import scine_utilities
from scine_parrot.lmlp_calculator import LmlpCalculator
from scine_parrot.ani_calculator import AniCalculator
from scine_parrot.m3gnet_calculator import M3gnetCalculator
from scine_parrot.mace_calculator import MaceCalculator


class ParrotModule(scine_utilities.core.Module):

    def __init__(self):
        super().__init__()
        self.__interfaces = ['calculator']
        self.__calculators = {
            'LMLP': LmlpCalculator,
            'ANI': AniCalculator,
            'M3GNET': M3gnetCalculator,
            'MACE': MaceCalculator
        }

    # ================================================================================ #
    #  The following functions have to be implemented to meet interface requirements!  #
    #  Do not change their signature!                                                  #
    #  They may be extended and adapted to do additional class-internal things.        #
    # ================================================================================ #

    def name(self):
        return 'Parrot'

    def get(self, interface: str, model: str):
        if interface.lower() != 'calculator':
            return None
        if model.upper() in self.__calculators:
            calc = self.__calculators[model.upper()]()
            return calc.shared_from_this()
        return None

    def has(self, interface: str, model: str):
        if interface.lower() not in self.__interfaces:
            return False
        if model.upper() in getattr(self, f'_{self.__class__.__name__}__{interface.lower()}s'):
            return True
        return False

    def announceInterfaces(self) -> List[str]:
        return self.__interfaces

    def announce_interfaces(self, *args, **kwargs) -> List[str]:
        return self.announceInterfaces(*args, **kwargs)

    def announceModels(self, interface: str) -> List[str]:
        if interface.lower() not in self.__interfaces:
            return []
        return list(getattr(self, f'_{self.__class__.__name__}__{interface.lower()}s').keys())

    def announce_models(self, *args, **kwargs) -> List[str]:
        return self.announceModels(*args, **kwargs)
