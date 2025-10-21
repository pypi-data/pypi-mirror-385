#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__copyright__ = """ This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Department of Chemistry and Applied Biosciences, Reiher Group.
See LICENSE.txt for details.
"""

import os
import shutil
import unittest
import numpy as np

from scine_parrot.module import ParrotModule
from scine_parrot.test.resources import path_test_resources
import scine_utilities as utils


class MaceCalculatorTest(unittest.TestCase):

    module_manager = utils.core.ModuleManager.get_instance()
    module_manager.load_module(ParrotModule())
    h2, _ = utils.io.read(os.path.join(path_test_resources(), 'h2.xyz'))
    ch4, _ = utils.io.read(os.path.join(path_test_resources(), 'ch4.xyz'))

    def test_module_loaded(self):
        assert self.module_manager.module_loaded('Parrot')

    def test_calculator_in_module(self):
        assert self.module_manager.has('calculator', 'mace')

    def test_load_calculator(self):
        _ = self.module_manager.get('calculator', 'mace')

    def test_h2_energy_mace_mp_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-mp_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -0.2433811632501, rtol=1e-5)

    def test_h2_gradients_mace_mp_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-mp_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.gradients[0][0] == 0.0
        assert results.gradients[1][0] == 0.0
        assert results.gradients[0][1] == 0.0
        assert results.gradients[1][1] == 0.0
        assert np.isclose(results.gradients[0][2], 0.00694938, rtol=1e-5)
        assert np.isclose(results.gradients[1][2], -0.00694938, rtol=1e-5)

    def test_h2_hessian_mace_mp_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-mp_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Hessian])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.hessian is not None
        for i in range(6):
            for j in range(6):
                if (i % 3) == (j % 3):
                    assert results.hessian[i][j] != 0.0
                else:
                    assert results.hessian[i][j] == 0.0
        assert results.thermochemistry is not None
        assert results.thermochemistry.overall.gibbs_free_energy != 0.0

    def test_h2_charges_mace_mp_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-mp_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.AtomicCharges])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.atomic_charges
        assert len(results.atomic_charges) == 2
        assert np.isclose(results.atomic_charges[0], 0.0, atol=1e-5)
        assert np.isclose(results.atomic_charges[1], 0.0, atol=1e-5)

    def test_h2_bond_order_mace_mp_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-mp_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.BondOrderMatrix])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.bond_orders
        assert results.bond_orders.get_order(0, 1) != 0.0
        assert results.bond_orders.get_order(0, 0) == 0.0
        assert results.bond_orders.get_order(1, 1) == 0.0

    def test_h2_readuct_optimization_mace_mp_large(self):
        import scine_readuct as readuct

        systems = {
            'guess': self.module_manager.get('calculator', 'mace'),
        }

        systems['guess'].structure = self.h2
        systems['guess'].settings['molecular_charge'] = 0
        systems['guess'].settings['spin_multiplicity'] = 1
        systems['guess'].settings['method'] = 'mace-mp_large'

        systems, success = readuct.run_optimization_task(
            systems,
            ['guess'],
            output=['opt'],
            stop_on_error=False,
            geoopt_coordinate_system='cartesianWithoutRotTrans',
            bfgs_trust_radius=0.3,
        )
        assert success
        shutil.rmtree('opt')

    def test_h2_energy_mace_mp_medium(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-mp_medium'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -0.2397350080295, rtol=1e-5)

    def test_h2_gradients_mace_mp_medium(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-mp_medium'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.gradients[0][0] == 0.0
        assert results.gradients[1][0] == 0.0
        assert results.gradients[0][1] == 0.0
        assert results.gradients[1][1] == 0.0
        assert np.isclose(results.gradients[0][2], 0.00533242, rtol=1e-5)
        assert np.isclose(results.gradients[1][2], -0.00533242, rtol=1e-5)

    def test_h2_energy_mace_mp_small(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-mp_small'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -0.2409101300737, rtol=1e-5)

    def test_h2_gradients_mace_mp_small(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-mp_small'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.gradients[0][0] == 0.0
        assert results.gradients[1][0] == 0.0
        assert results.gradients[0][1] == 0.0
        assert results.gradients[1][1] == 0.0
        assert np.isclose(results.gradients[0][2], 0.00829265, rtol=1e-5)
        assert np.isclose(results.gradients[1][2], -0.00829265, rtol=1e-5)

    def test_h2_energy_mace_off_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-off_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -1.1710190352478, rtol=1e-5)

    def test_h2_gradients_mace_off_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-off_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.gradients[0][0] == 0.0
        assert results.gradients[1][0] == 0.0
        assert results.gradients[0][1] == 0.0
        assert results.gradients[1][1] == 0.0
        assert np.isclose(results.gradients[0][2], -0.00629718, rtol=1e-5)
        assert np.isclose(results.gradients[1][2], 0.00629718, rtol=1e-5)

    def test_h2_hessian_mace_off_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-off_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Hessian])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.hessian is not None
        for i in range(6):
            for j in range(6):
                if (i % 3) == (j % 3):
                    assert results.hessian[i][j] != 0.0
                else:
                    assert results.hessian[i][j] == 0.0
        assert results.thermochemistry is not None
        assert results.thermochemistry.overall.gibbs_free_energy != 0.0

    def test_h2_charges_mace_off_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-off_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.AtomicCharges])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.atomic_charges
        assert len(results.atomic_charges) == 2
        assert np.isclose(results.atomic_charges[0], 0.0, atol=1e-5)
        assert np.isclose(results.atomic_charges[1], 0.0, atol=1e-5)

    def test_h2_bond_order_mace_off_large(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-off_large'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.BondOrderMatrix])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.bond_orders
        assert results.bond_orders.get_order(0, 1) != 0.0
        assert results.bond_orders.get_order(0, 0) == 0.0
        assert results.bond_orders.get_order(1, 1) == 0.0

    def test_h2_readuct_optimization_mace_off_large(self):
        import scine_readuct as readuct

        systems = {
            'guess': self.module_manager.get('calculator', 'mace'),
        }

        systems['guess'].structure = self.h2
        systems['guess'].settings['molecular_charge'] = 0
        systems['guess'].settings['spin_multiplicity'] = 1
        systems['guess'].settings['method'] = 'mace-off_large'

        systems, success = readuct.run_optimization_task(
            systems,
            ['guess'],
            output=['opt'],
            stop_on_error=False,
            geoopt_coordinate_system='cartesianWithoutRotTrans',
            bfgs_trust_radius=0.3,
        )
        assert success
        shutil.rmtree('opt')

    def test_h2_energy_mace_off_medium(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-off_medium'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -1.1705010422918, rtol=1e-5)

    def test_h2_gradients_mace_off_medium(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-off_medium'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.gradients[0][0] == 0.0
        assert results.gradients[1][0] == 0.0
        assert results.gradients[0][1] == 0.0
        assert results.gradients[1][1] == 0.0
        assert np.isclose(results.gradients[0][2], -0.01203343, rtol=1e-5)
        assert np.isclose(results.gradients[1][2], 0.01203343, rtol=1e-5)

    def test_h2_energy_mace_off_small(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-off_small'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -1.1703778875390, rtol=1e-5)

    def test_h2_gradients_mace_off_small(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'mace-off_small'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.gradients[0][0] == 0.0
        assert results.gradients[1][0] == 0.0
        assert results.gradients[0][1] == 0.0
        assert results.gradients[1][1] == 0.0
        assert np.isclose(results.gradients[0][2], -0.00700337, rtol=1e-5)
        assert np.isclose(results.gradients[1][2], 0.00700337, rtol=1e-5)

    def test_ch4_energy(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.ch4
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -0.8470963108369, rtol=1e-5)

    def test_ch4_gradients(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.ch4
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        gradients_ref = np.array([[-0.04355574, 0.06505702, 0.02412450],
                                  [0.07390137, -0.06888232, 0.03614215],
                                  [-0.02857420, 0.01394650, -0.01493549],
                                  [-0.01201121, -0.00647844, -0.02058262],
                                  [0.01023979, -0.00364276, -0.02474853]])
        assert np.all(np.isclose(results.gradients, gradients_ref, rtol=1e-5))

    def test_ch4_hessian(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.ch4
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Hessian])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.hessian is not None
        assert np.all(results.hessian != 0.0)
        assert results.thermochemistry is not None
        assert results.thermochemistry.overall.gibbs_free_energy != 0.0

    def test_ch4_charges(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.ch4
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.AtomicCharges])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.atomic_charges
        assert len(results.atomic_charges) == 5
        atomic_charges_ref = np.array([-0.1881777989596,
                                       0.0583404661627,
                                       0.0473636686695,
                                       0.0513217113314,
                                       0.0311519527961])
        assert np.all(np.isclose(results.atomic_charges, atomic_charges_ref, rtol=1e-5))

    def test_ch4_bond_order(self):
        calculator = self.module_manager.get('calculator', 'mace')
        assert calculator is not None
        calculator.structure = self.ch4
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.BondOrderMatrix])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.bond_orders
        for i in range(1, 5):
            assert results.bond_orders.get_order(0, i) != 0.0
        for i in range(5):
            assert results.bond_orders.get_order(i, i) == 0.0

    def test_ch4_readuct_optimization(self):
        import scine_readuct as readuct

        systems = {
            'guess': self.module_manager.get('calculator', 'mace'),
        }

        systems['guess'].structure = self.ch4
        systems['guess'].settings['molecular_charge'] = 0
        systems['guess'].settings['spin_multiplicity'] = 1

        systems, success = readuct.run_optimization_task(
            systems,
            ['guess'],
            output=['opt'],
            stop_on_error=False,
            geoopt_coordinate_system='cartesianWithoutRotTrans',
            bfgs_trust_radius=0.3,
        )
        assert success
        shutil.rmtree('opt')
