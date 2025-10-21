#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__copyright__ = """ This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Department of Chemistry and Applied Biosciences, Reiher Group.
See LICENSE.txt for details.
"""


from os import path
from copy import copy
import numpy as np

import scine_utilities as utils
from scine_utilities import Results

from scine_parrot.lmlp import lMLP
from scine_parrot.calculator import GFN2EnhancedCalculator
from scine_parrot.resources import resource_path


class LmlpCalculator(GFN2EnhancedCalculator):

    _lmlp: lMLP
    _method = ''

    def __init__(self):
        super().__init__()
        self._settings['method'] = path.join(resource_path(), 'lmlp/lMLP-SN2.ini')
        self.lmlp: lMLP

    def __resolve_method(self) -> lMLP:
        if LmlpCalculator._method != self._settings['method']:
            LmlpCalculator._method = self._settings['method']
            LmlpCalculator._lmlp = lMLP(generalization_setting_file=self._settings['method'])
        return LmlpCalculator._lmlp

    def _calculate_impl(self, _: str = '') -> Results:
        self._results = Results()

        assert self.get_possible_properties().contains_subset(
            self._required_properties
        )

        self.lmlp = self.__resolve_method()

        if self._structure is None:
            raise RuntimeError('Called calculate() without structure in calculator.')
        elements = np.array([utils.ElementInfo.symbol(e) for e in self._structure.elements])
        positions = self._structure.positions

        # Energies and Gradients
        requires_energy = self._required_properties.contains_subset(
            utils.PropertyList(utils.Property.Energy)
        )
        requires_gradients = self._required_properties.contains_subset(
            utils.PropertyList(utils.Property.Gradients)
        )
        # Hessian and thermo-chemistry
        requires_hessian = self._required_properties.contains_subset(
            utils.PropertyList(utils.Property.Hessian)
        )
        requires_thermo = self._required_properties.contains_subset(
            utils.PropertyList(utils.Property.Thermochemistry)
        )
        if requires_energy and not (requires_gradients or requires_hessian or requires_thermo):
            self._results.energy = self.lmlp.predict(elements, positions, calc_forces=False)
            self._results.successful_calculation = True

        elif requires_gradients or requires_hessian or requires_thermo:
            self._results.energy, self._results.gradients = self.lmlp.predict(elements, positions)
            self._results.successful_calculation = True

        if requires_hessian or requires_thermo:
            self.__calculate_hessian(elements, positions)
            assert self._results.hessian is not None
            assert self._results.energy is not None
            thermo = utils.ThermochemistryCalculator(
                self._results.hessian,
                self._structure,
                self._settings['spin_multiplicity'],
                self._results.energy
            )
            thermo.set_temperature(self._settings['temperature'])
            thermo.set_pressure(self._settings['pressure'])
            thermo.set_molecular_symmetry(self._settings['symmetry_number'])
            self._results.thermochemistry = thermo.calculate()
            self._results.successful_calculation = True

        # If charges or bond orders are required, fall back to GFN2 for these properties
        requires_charges = self._required_properties.contains_subset(
            utils.PropertyList(utils.Property.AtomicCharges)
        )
        requires_bond_orders = self._required_properties.contains_subset(
            utils.PropertyList(utils.Property.BondOrderMatrix)
        )
        if requires_charges or requires_bond_orders:
            self._add_gfn2_data()

        self._results.program_name = 'parrot'
        self._results.description = 'LmlpCalculation'
        return self._results

    def __calculate_hessian(self, elements, input_positions, delta=0.01) -> None:
        positions = copy(input_positions)
        n_atoms = len(positions)
        hessian = np.zeros(shape=(3 * n_atoms, 3 * n_atoms))
        for dir in range(3):
            for atom in range(n_atoms):
                positions[atom][dir] += delta
                _, gradients = self.lmlp.predict(elements, positions)
                for j in range(n_atoms):
                    hessian[(3 * atom + dir)][(3 * j):(3 * j + 3)] += gradients[j]
                positions[atom][dir] -= 2.0 * delta
                _, gradients = self.lmlp.predict(elements, positions)
                for j in range(n_atoms):
                    hessian[(3 * atom + dir)][(3 * j):(3 * j + 3)] -= gradients[j]
                positions[atom][dir] += delta
        hessian /= 2.0 * delta
        self._results.hessian = (hessian + hessian.T) / 2.0  # symmetrize

    def _name_impl(self) -> str:
        return 'ParrotLmlpCalculator'

    def _possible_properties_impl(self) -> utils.PropertyList:
        pl = utils.PropertyList(utils.Property.Energy)
        pl.add_property(utils.Property.Gradients)
        pl.add_property(utils.Property.Hessian)
        pl.add_property(utils.Property.Thermochemistry)
        pl.add_property(utils.Property.AtomicCharges)
        pl.add_property(utils.Property.BondOrderMatrix)
        pl.add_property(utils.Property.SuccessfulCalculation)
        pl.add_property(utils.Property.ProgramName)
        pl.add_property(utils.Property.Description)
        return pl

    def _supports_method_family_impl(self, method_family: str) -> bool:
        if method_family.lower() == 'lmlp':
            return True
        return False
