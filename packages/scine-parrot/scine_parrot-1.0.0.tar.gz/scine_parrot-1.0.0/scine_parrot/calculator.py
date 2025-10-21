#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__copyright__ = """ This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Department of Chemistry and Applied Biosciences, Reiher Group.
See LICENSE.txt for details.
"""

from abc import abstractmethod
from typing import Optional
from copy import copy

import scine_xtb_wrapper  # noqa: F401 , pylint: disable=unused-import

import scine_utilities as utils

from scine_utilities import (
    AtomCollection,
    Results,
)


class CalculatorState(utils.core.State):

    def __init__(self, structure: AtomCollection, settings):
        super().__init__()
        self.structure = structure
        self.settings = settings


class GFN2EnhancedCalculator(utils.core.Calculator):

    def __init__(self):
        super().__init__()
        module_manager = utils.core.ModuleManager.get_instance()
        self._gfn2 = module_manager.get('calculator', 'gfn2')
        self._gfn2.set_required_properties([
            utils.Property.Energy,
            utils.Property.AtomicCharges,
            utils.Property.BondOrderMatrix,
        ])
        self._settings = utils.Settings(self._gfn2.settings.descriptor_collection)
        self._results = Results()
        self._structure: Optional[AtomCollection] = None
        self._required_properties = utils.PropertyList()

    @abstractmethod
    def _calculate_impl(self, _: str = '') -> Results:
        raise NotImplementedError

    @abstractmethod
    def _name_impl(self):
        raise NotImplementedError

    @abstractmethod
    def _supports_method_family_impl(self, method_family: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _possible_properties_impl(self):
        raise NotImplementedError

    def _set_required_properties_impl(self, new) -> None:
        if self.get_possible_properties().contains_subset(new):
            self._required_properties = new
        else:
            raise RuntimeError('Error: Some of the requested Properties can not be provided')

    def _add_gfn2_data(self):
        self._gfn2.structure = self._structure
        tmp = copy(dict(self._settings))
        tmp.pop('method')
        for key in tmp:
            self._gfn2.settings[key] = tmp[key]
        gfn2_results = self._gfn2.calculate()
        self._results.successful_calculation = gfn2_results.successful_calculation
        self._results.atomic_charges = gfn2_results.atomic_charges
        self._results.bond_orders = gfn2_results.bond_orders

    def _set_structure_impl(self, new_structure: AtomCollection):
        self._structure = new_structure

    def _get_structure_impl(self):
        return self._structure

    def _modify_positions_impl(self, new_positions):
        self._structure.positions = new_positions

    def _get_positions_impl(self):
        return self._structure.positions

    def _get_required_properties_impl(self):
        return self._required_properties

    def _settings_impl(self):
        return self._settings

    def _results_impl(self) -> Results:
        return self._results

    def _load_state_impl(self, state: utils.core.State):
        if not isinstance(state, CalculatorState):
            raise RuntimeError('Error: Tried loading state of wrong calculator.')
        self._structure = state.structure
        self._settings = state.settings

    # def init_from_other(self, other: 'GFN2EnhancedCalculator'):
    #     self._settings = copy(other.settings)
    #     self._results = other.results()
    #     self._structure = other.getStructure()

    def __copy__(self):
        other = self.__class__()
        for key in dict(self._settings):
            other.settings[key] = self._settings[key]
        other._structure = self._structure
        return other

    def _clone_impl(self):
        other = self.__class__()
        for key in dict(self._settings):
            other.settings[key] = self._settings[key]
        other._structure = self._structure
        return other

    def _allows_python_gil_release_impl(self):
        return False
