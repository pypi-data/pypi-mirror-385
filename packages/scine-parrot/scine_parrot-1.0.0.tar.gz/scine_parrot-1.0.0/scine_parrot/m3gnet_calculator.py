#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__copyright__ = """ This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Department of Chemistry and Applied Biosciences, Reiher Group.
See LICENSE.txt for details.
"""


from typing import Optional
from copy import copy
import numpy as np

import scine_utilities as utils
from scine_utilities import Results

import torch
import matgl
from matgl.ext.ase import M3GNetCalculator as ASEM3GNetCalculator
from ase import Atoms

from scine_parrot.calculator import GFN2EnhancedCalculator


class M3gnetCalculator(GFN2EnhancedCalculator):

    _m3gnet_mp_202128_pes: Optional[ASEM3GNetCalculator] = None
    _m3gnet_mp_202128_direct_pes: Optional[ASEM3GNetCalculator] = None

    def __init__(self):
        super().__init__()
        torch.set_default_dtype(torch.float)
        self._settings['method'] = 'm3gnet-mp-2021.2.8-pes'
        self.m3gnet: ASEM3GNetCalculator

    def __resolve_method(self) -> ASEM3GNetCalculator:
        if self._settings['method'] == 'm3gnet-mp-2021.2.8-pes':
            if M3gnetCalculator._m3gnet_mp_202128_pes is None:
                for fn in ('model.pt', 'state.pt', 'model.json'):
                    matgl.utils.io.RemoteFile(
                        f'https://github.com/materialsvirtuallab/matgl/raw/v{matgl.__version__}/'
                        + f'pretrained_models/M3GNet-MP-2021.2.8-PES/{fn}')
                M3gnetCalculator._m3gnet_mp_202128_pes = ASEM3GNetCalculator(
                    matgl.load_model('M3GNet-MP-2021.2.8-PES'))
            return M3gnetCalculator._m3gnet_mp_202128_pes
        if self._settings['method'] == 'm3gnet-mp-2021.2.8-direct-pes':
            if M3gnetCalculator._m3gnet_mp_202128_direct_pes is None:
                for fn in ('model.pt', 'state.pt', 'model.json'):
                    matgl.utils.io.RemoteFile(
                        f'https://github.com/materialsvirtuallab/matgl/raw/v{matgl.__version__}'
                        + f'/pretrained_models/M3GNet-MP-2021.2.8-DIRECT-PES/{fn}')
                M3gnetCalculator._m3gnet_mp_202128_direct_pes = ASEM3GNetCalculator(
                    matgl.load_model('M3GNet-MP-2021.2.8-DIRECT-PES'))
            return M3gnetCalculator._m3gnet_mp_202128_direct_pes
        raise RuntimeError(
            f'Requested method {self._settings["method"]} is not available in Parrot::M3gnetCalculator'
        )

    def _calculate_impl(self, _: str = '') -> Results:
        self._results = Results()

        assert self.get_possible_properties().contains_subset(
            self._required_properties
        )

        self.m3gnet = self.__resolve_method()

        if self._structure is None:
            raise RuntimeError('Called calculate() without structure in calculator.')
        elements = np.array([utils.ElementInfo.symbol(e) for e in self._structure.elements])
        positions = self._structure.positions * utils.ANGSTROM_PER_BOHR
        atoms = Atoms(elements, positions)
        atoms.calc = self.m3gnet

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
            self._results.energy = np.squeeze(atoms.get_potential_energy()) * utils.HARTREE_PER_EV
            self._results.successful_calculation = True

        elif requires_gradients or requires_hessian or requires_thermo:
            self._results.energy = np.squeeze(atoms.get_potential_energy()) * utils.HARTREE_PER_EV
            self._results.gradients = -atoms.get_forces() * utils.HARTREE_PER_EV * utils.ANGSTROM_PER_BOHR
            self._results.successful_calculation = True

        if requires_hessian or requires_thermo:
            self.__calculate_hessian(atoms)
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
        self._results.description = 'M3gnetCalculation'
        return self._results

    def __calculate_hessian(self, atoms, delta=0.01) -> None:
        positions = atoms.get_positions()
        input_positions = copy(positions)
        n_atoms = len(positions)
        hessian = np.zeros(shape=(3 * n_atoms, 3 * n_atoms))
        for dir in range(3):
            for atom in range(n_atoms):
                positions[atom][dir] += delta * utils.ANGSTROM_PER_BOHR
                atoms.set_positions(positions)
                gradients = -atoms.get_forces() * utils.HARTREE_PER_EV * utils.ANGSTROM_PER_BOHR
                for j in range(n_atoms):
                    hessian[(3 * atom + dir)][(3 * j):(3 * j + 3)] += gradients[j]
                positions[atom][dir] -= 2.0 * delta * utils.ANGSTROM_PER_BOHR
                atoms.set_positions(positions)
                gradients = -atoms.get_forces() * utils.HARTREE_PER_EV * utils.ANGSTROM_PER_BOHR
                for j in range(n_atoms):
                    hessian[(3 * atom + dir)][(3 * j):(3 * j + 3)] -= gradients[j]
                positions[atom][dir] += delta * utils.ANGSTROM_PER_BOHR
        hessian /= 2.0 * delta
        atoms.set_positions(input_positions)
        self._results.hessian = (hessian + hessian.T) / 2.0  # symmetrize

    def _name_impl(self) -> str:
        return 'ParrotM3gnetCalculator'

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
        if method_family.lower() == 'm3gnet':
            return True
        return False
