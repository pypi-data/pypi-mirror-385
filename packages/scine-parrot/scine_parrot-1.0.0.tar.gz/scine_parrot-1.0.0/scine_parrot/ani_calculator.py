#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__copyright__ = """ This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Department of Chemistry and Applied Biosciences, Reiher Group.
See LICENSE.txt for details.
"""


from typing import Optional, Union
import warnings
import numpy as np

import scine_utilities as utils
from scine_utilities import Results

import torch
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', message='cuaev not installed')
    warnings.filterwarnings('ignore', message='Dependency not satisfied, torchani.data will not be available')
    from torchani.models import ANI2x, ANI1ccx, ANI1x
from scine_parrot.calculator import GFN2EnhancedCalculator


class AniCalculator(GFN2EnhancedCalculator):

    _ani2x: Optional[ANI2x] = None
    _ani1ccx: Optional[ANI1ccx] = None
    _ani1x: Optional[ANI1x] = None

    def __init__(self):
        super().__init__()
        self._settings['method'] = 'ani2x'
        self.ani: Union[ANI2x, ANI1ccx, ANI1x]

    def __resolve_method(self) -> Union[ANI2x, ANI1ccx, ANI1x]:
        if self._settings['method'] == 'ani2x':
            if AniCalculator._ani2x is None:
                AniCalculator._ani2x = ANI2x(periodic_table_index=True)
            return AniCalculator._ani2x
        if self._settings['method'] == 'ani1ccx':
            if AniCalculator._ani1ccx is None:
                AniCalculator._ani1ccx = ANI1ccx(periodic_table_index=True)
            return AniCalculator._ani1ccx
        if self._settings['method'] == 'ani1x':
            if AniCalculator._ani1x is None:
                AniCalculator._ani1x = ANI1x(periodic_table_index=True)
            return AniCalculator._ani1x
        raise RuntimeError(
            f'Requested method {self._settings["method"]} is not available in Parrot::AniCalculator'
        )

    def _calculate_impl(self, _: str = '') -> Results:
        self._results = Results()

        assert self.get_possible_properties().contains_subset(
            self._required_properties
        )

        self.ani = self.__resolve_method()

        if self._structure is None:
            raise RuntimeError('Called calculate() without structure in calculator.')
        elements = torch.tensor(
            [[utils.ElementInfo.Z(e) for e in self._structure.elements]]
        )
        positions = torch.tensor(
            np.array([self._structure.positions * utils.ANGSTROM_PER_BOHR]),
            requires_grad=True,
            dtype=torch.float32
        )

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
            energies = self.ani((elements, positions)).energies
            self._results.energy = energies.item()
            self._results.successful_calculation = True

        elif requires_gradients or requires_hessian or requires_thermo:
            energies = self.ani((elements, positions)).energies
            self._results.energy = energies.item()
            self._results.gradients = torch.autograd.grad(
                energies.sum(), positions
            )[0].squeeze().detach().numpy() * utils.ANGSTROM_PER_BOHR
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
        self._results.description = 'AniCalculation'
        return self._results

    def __calculate_hessian(self, elements, input_positions, delta=0.01) -> None:
        positions = torch.clone(input_positions)
        n_atoms = len(positions[0])
        hessian = np.zeros(shape=(3 * n_atoms, 3 * n_atoms))
        for dir in range(3):
            for atom in range(n_atoms):
                positions[0][atom][dir] += delta * utils.ANGSTROM_PER_BOHR
                energies = self.ani((elements, positions)).energies
                gradients = torch.autograd.grad(
                    energies.sum(), positions
                )[0].squeeze().detach().numpy() * utils.ANGSTROM_PER_BOHR
                for j in range(n_atoms):
                    hessian[(3 * atom + dir)][(3 * j):(3 * j + 3)] += gradients[j]
                positions[0][atom][dir] -= 2.0 * delta * utils.ANGSTROM_PER_BOHR
                energies = self.ani((elements, positions)).energies
                gradients = torch.autograd.grad(
                    energies.sum(), positions
                )[0].squeeze().detach().numpy() * utils.ANGSTROM_PER_BOHR
                for j in range(n_atoms):
                    hessian[(3 * atom + dir)][(3 * j):(3 * j + 3)] -= gradients[j]
                positions[0][atom][dir] += delta * utils.ANGSTROM_PER_BOHR
        hessian /= 2.0 * delta
        self._results.hessian = (hessian + hessian.T) / 2.0  # symmetrize

    def _name_impl(self) -> str:
        return 'ParrotAniCalculator'

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
        if method_family.lower() == 'ani':
            return True
        return False
