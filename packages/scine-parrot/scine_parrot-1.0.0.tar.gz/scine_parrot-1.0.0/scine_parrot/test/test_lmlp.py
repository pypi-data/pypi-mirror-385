#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__copyright__ = """ This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Department of Chemistry and Applied Biosciences, Reiher Group.
See LICENSE.txt for details.
"""

from os import remove
import unittest
import numpy as np
from torch import load
from scine_parrot.lmlp import lMLP
from scine_parrot.test.resources import path_test_resources

RESOURCES_DIR = f'{path_test_resources()}/lmlp'


class LmlpTest(unittest.TestCase):

    Bohr2Angstrom = 0.529177210903   # CODATA 2018
    Hartree2eV = 27.211386245988   # CODATA 2018

    def test_1_molecule_only_energy(self) -> None:
        '''
        Test 1: QM energy prediction of molecular system
                (full description of settings is available in test_1.ini)
        '''
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_1.ini')
        checkpoint = load(f'{RESOURCES_DIR}/test_1_data.pt', weights_only=False)
        elements = checkpoint['elements']
        positions = checkpoint['positions'] / self.Bohr2Angstrom
        energy_prediction = checkpoint['energy_prediction'] / self.Hartree2eV
        energy = lmlp.predict(elements, positions, calc_forces=False)
        assert np.isclose(energy, energy_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy is {energy} but it should be {energy_prediction}.'

    def test_2_molecule_only_radial(self) -> None:
        '''
        Test 2: QM energy and gradients prediction of molecular system (only radial descriptors)
                (full description of settings is available in test_2.ini)
        '''
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_2.ini')
        checkpoint = load(f'{RESOURCES_DIR}/test_2_data.pt', weights_only=False)
        elements = checkpoint['elements']
        positions = checkpoint['positions'] / self.Bohr2Angstrom
        energy_prediction = checkpoint['energy_prediction'] / self.Hartree2eV
        gradients_prediction = -checkpoint['forces_prediction'] / self.Hartree2eV * self.Bohr2Angstrom
        energy, gradients = lmlp.predict(elements, positions)
        assert np.isclose(energy, energy_prediction, rtol=1e-5, atol=1e-5), \
            f'ERROR: Energy is {energy} but it should be {energy_prediction}.'
        assert np.allclose(gradients, gradients_prediction, rtol=1e-5, atol=1e-5), \
            f'ERROR: Gradients are {gradients} but they should be {gradients_prediction}.'

    def test_3_periodic(self) -> None:
        '''
        Test 3: QM energy and gradients prediction of periodic system
                (full description of settings is available in test_3.ini)
        '''
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_3.ini')
        checkpoint = load(f'{RESOURCES_DIR}/test_3_data.pt', weights_only=False)
        elements = checkpoint['elements']
        positions = checkpoint['positions'] / self.Bohr2Angstrom
        lattices = checkpoint['lattices'] / self.Bohr2Angstrom
        energy_prediction = checkpoint['energy_prediction'] / self.Hartree2eV
        gradients_prediction = -checkpoint['forces_prediction'] / self.Hartree2eV * self.Bohr2Angstrom
        energy, gradients = lmlp.predict(elements, positions, lattices)
        assert np.isclose(energy, energy_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy is {energy} but it should be {energy_prediction}.'
        assert np.allclose(gradients, gradients_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Gradients are {gradients} but they should be {gradients_prediction}.'

    def test_4_QMMM(self) -> None:
        '''
        Test 4: QM/MM energy and gradients prediction of molecular system
                (full description of settings is available in test_4.ini)
        '''
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_4.ini')
        checkpoint = load(f'{RESOURCES_DIR}/test_4_data.pt', weights_only=False)
        elements = checkpoint['elements']
        positions = checkpoint['positions'] / self.Bohr2Angstrom
        atomic_classes = checkpoint['atomic_classes']
        atomic_charges = checkpoint['atomic_charges']
        energy_prediction = checkpoint['energy_prediction'] / self.Hartree2eV
        gradients_prediction = -checkpoint['forces_prediction'] / self.Hartree2eV * self.Bohr2Angstrom
        energy, gradients = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges)
        assert np.isclose(energy, energy_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy is {energy} but it should be {energy_prediction}.'
        assert np.allclose(gradients, gradients_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Gradients are {gradients} but they should be {gradients_prediction}.'

    def test_5_QMMM_only_radial(self) -> None:
        '''
        Test 5: QM/MM energy and gradients prediction of molecular system (only radial descriptors)
                (full description of settings is available in test_5.ini)
        '''
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_5.ini')
        checkpoint = load(f'{RESOURCES_DIR}/test_5_data.pt', weights_only=False)
        elements = checkpoint['elements']
        positions = checkpoint['positions'] / self.Bohr2Angstrom
        atomic_classes = checkpoint['atomic_classes']
        atomic_charges = checkpoint['atomic_charges']
        energy_prediction = checkpoint['energy_prediction'] / self.Hartree2eV
        gradients_prediction = -checkpoint['forces_prediction'] / self.Hartree2eV * self.Bohr2Angstrom
        energy, gradients = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges)
        assert np.isclose(energy, energy_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy is {energy} but it should be {energy_prediction}.'
        assert np.allclose(gradients, gradients_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Gradients are {gradients} but they should be {gradients_prediction}.'

    def test_6_molecule_uncertainty(self) -> None:
        '''
        Test 6: QM energy and gradients prediction including uncertainties of molecular system
                (full description of settings is available in test_6.ini)
        '''
        checkpoint = load(f'{RESOURCES_DIR}/test_6_data.pt', weights_only=False)
        elements = checkpoint['elements']
        positions = checkpoint['positions'] / self.Bohr2Angstrom
        energy_prediction = checkpoint['energy_prediction'] / self.Hartree2eV
        gradients_prediction = -checkpoint['forces_prediction'] / self.Hartree2eV * self.Bohr2Angstrom
        energy_uncertainty_1 = checkpoint['energy_uncertainty_1'] / self.Hartree2eV
        gradients_uncertainty_1 = checkpoint['forces_uncertainty_1'] / self.Hartree2eV * self.Bohr2Angstrom
        energy_uncertainty_2 = checkpoint['energy_uncertainty_2'] / self.Hartree2eV
        gradients_uncertainty_2 = checkpoint['forces_uncertainty_2'] / self.Hartree2eV * self.Bohr2Angstrom
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_6.ini',
                    uncertainty_scaling=20.0, uncertainty_thresholds=(300.0, 300.0, 300.0))
        energy, energy_uncertainty = lmlp.predict(
            elements, positions, calc_forces=False, calc_uncertainty=True)
        energy, gradients, energy_uncertainty, gradients_uncertainty = lmlp.predict(
            elements, positions, calc_uncertainty=True)
        assert np.isclose(energy, energy_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy is {energy} but it should be {energy_prediction}.'
        assert np.allclose(gradients, gradients_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Gradients are {gradients} but they should be {gradients_prediction}.'
        assert np.isclose(energy_uncertainty, energy_uncertainty_1, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy uncertainty is {energy_uncertainty} but it should be {energy_uncertainty_1}.'
        assert np.allclose(gradients_uncertainty, gradients_uncertainty_1, rtol=1e-5, atol=1e-8), \
            f'ERROR: Force uncertainties are {gradients_uncertainty} but they should be {gradients_uncertainty_1}.'
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_6.ini',
                    uncertainty_thresholds=(300.0, 300.0, 300.0),
                    active_learning_file=f'{RESOURCES_DIR}/input.data_active_learning_tmp',
                    active_learning_thresholds=(0.0, 3.0, 3.0),
                    active_learning_min_step_difference=0)
        energy, gradients, energy_uncertainty, gradients_uncertainty = lmlp.predict(
            elements, positions, name='1')
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_6.ini',
                    uncertainty_thresholds=(300.0, 300.0, 300.0),
                    active_learning_file=f'{RESOURCES_DIR}/input.data_active_learning_tmp',
                    active_learning_thresholds=(3.0, 0.0, 3.0),
                    active_learning_min_step_difference=0)
        energy, gradients, energy_uncertainty, gradients_uncertainty = lmlp.predict(
            elements, positions, name='1')
        assert np.isclose(energy_uncertainty, energy_uncertainty_2, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy uncertainty is {energy_uncertainty} but it should be {energy_uncertainty_2}.'
        assert np.allclose(gradients_uncertainty, gradients_uncertainty_2, rtol=1e-5, atol=1e-8), \
            f'ERROR: Force uncertainties are {gradients_uncertainty} but they should be {gradients_uncertainty_2}.'
        remove(f'{RESOURCES_DIR}/input.data_active_learning_tmp')

    def test_7_QMMM_uncertainty(self) -> None:
        '''
        Test 7: QM/MM energy and gradients prediction including uncertainties of molecular system
                (full description of settings is available in test_7.ini)
        '''
        checkpoint = load(f'{RESOURCES_DIR}/test_7_data.pt', weights_only=False)
        elements = checkpoint['elements']
        positions = checkpoint['positions'] / self.Bohr2Angstrom
        atomic_classes = checkpoint['atomic_classes']
        atomic_charges = checkpoint['atomic_charges']
        energy_prediction = checkpoint['energy_prediction'] / self.Hartree2eV
        gradients_prediction = -checkpoint['forces_prediction'] / self.Hartree2eV * self.Bohr2Angstrom
        energy_uncertainty_1 = checkpoint['energy_uncertainty_1'] / self.Hartree2eV
        gradients_uncertainty_1 = checkpoint['forces_uncertainty_1'] / self.Hartree2eV * self.Bohr2Angstrom
        energy_uncertainty_2 = checkpoint['energy_uncertainty_2'] / self.Hartree2eV
        gradients_uncertainty_2 = checkpoint['forces_uncertainty_2'] / self.Hartree2eV * self.Bohr2Angstrom
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_7.ini',
                    uncertainty_scaling=1000.0, uncertainty_thresholds=(0.3, 3000.0, 3000.0))
        energy, energy_uncertainty = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges,
            calc_forces=False, calc_uncertainty=True)
        assert np.isnan(energy), f'ERROR: Energy is {energy} but it should be {np.nan}.'
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_7.ini',
                    uncertainty_scaling=1000.0, uncertainty_thresholds=(3000.0, 3.0, 3000.0))
        energy, gradients, energy_uncertainty, gradients_uncertainty = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges,
            calc_uncertainty=True)
        assert np.all(np.isnan(gradients)), f'ERROR: Gradients are {gradients} but they should be all {np.nan}.'
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_7.ini',
                    uncertainty_scaling=1000.0, uncertainty_thresholds=(3000.0, 3000.0, 3.0))
        energy, gradients, energy_uncertainty, gradients_uncertainty = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges,
            calc_uncertainty=True)
        assert np.all(np.isnan(gradients)), f'ERROR: Gradients are {gradients} but they should be all {np.nan}.'
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_7.ini',
                    uncertainty_scaling=1000.0, uncertainty_thresholds=(3000.0, 3000.0, 3000.0))
        energy, gradients, energy_uncertainty, gradients_uncertainty = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges,
            calc_uncertainty=True)
        assert np.isclose(energy, energy_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy is {energy} but it should be {energy_prediction}.'
        assert np.allclose(gradients, gradients_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Gradients are {gradients} but they should be {gradients_prediction}.'
        assert np.isclose(energy_uncertainty, energy_uncertainty_1, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy uncertainty is {energy_uncertainty} but it should be {energy_uncertainty_1}.'
        assert np.allclose(gradients_uncertainty, gradients_uncertainty_1, rtol=1e-5, atol=1e-8), \
            f'ERROR: Force uncertainties are {gradients_uncertainty} but they should be {gradients_uncertainty_1}.'
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_7.ini',
                    uncertainty_thresholds=(300.0, 300.0, 300.0),
                    active_learning_file=f'{RESOURCES_DIR}/input.data_active_learning_tmp',
                    active_learning_thresholds=(0.0, 3.0, 3.0),
                    active_learning_max_number=1,
                    active_learning_min_step_difference=1,
                    active_learning_min_atom_distance=-1.0)
        energy, energy_uncertainty = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges, name='1',
            calc_forces=False)
        assert np.isclose(energy, energy_prediction, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy is {energy} but it should be {energy_prediction}.'
        energy, energy_uncertainty = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges, name='1',
            calc_forces=False)
        assert np.isnan(energy), f'ERROR: Energy is {energy} but it should be {np.nan}.'
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_7.ini',
                    uncertainty_thresholds=(300.0, 300.0, 300.0),
                    active_learning_file=f'{RESOURCES_DIR}/input.data_active_learning_tmp',
                    active_learning_thresholds=(0.0, 3.0, 3.0),
                    active_learning_max_number=100,
                    active_learning_min_step_difference=0,
                    active_learning_min_atom_distance=10.0)
        energy, energy_uncertainty = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges, name='1',
            calc_forces=False)
        assert np.isnan(energy), f'ERROR: Energy is {energy} but it should be {np.nan}.'
        lmlp = lMLP(generalization_setting_file=f'{RESOURCES_DIR}/test_7.ini',
                    uncertainty_thresholds=(300.0, 300.0, 300.0),
                    active_learning_file=f'{RESOURCES_DIR}/input.data_active_learning_tmp',
                    active_learning_thresholds=(3.0, 0.0, 3.0),
                    active_learning_min_step_difference=0)
        energy, gradients, energy_uncertainty, gradients_uncertainty = lmlp.predict(
            elements, positions, atomic_classes=atomic_classes, atomic_charges=atomic_charges, name='1')
        assert np.isclose(energy_uncertainty, energy_uncertainty_2, rtol=1e-5, atol=1e-8), \
            f'ERROR: Energy uncertainty is {energy_uncertainty} but it should be {energy_uncertainty_2}.'
        assert np.allclose(gradients_uncertainty, gradients_uncertainty_2, rtol=1e-5, atol=1e-8), \
            f'ERROR: Force uncertainties are {gradients_uncertainty} but they should be {gradients_uncertainty_2}.'
        remove(f'{RESOURCES_DIR}/input.data_active_learning_tmp')
