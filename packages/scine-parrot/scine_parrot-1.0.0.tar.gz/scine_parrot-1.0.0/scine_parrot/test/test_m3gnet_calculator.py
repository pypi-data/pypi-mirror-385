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


class M3gnetCalculatorTest(unittest.TestCase):

    module_manager = utils.core.ModuleManager.get_instance()
    module_manager.load_module(ParrotModule())
    h2, _ = utils.io.read(os.path.join(path_test_resources(), 'h2.xyz'))
    ch4, _ = utils.io.read(os.path.join(path_test_resources(), 'ch4.xyz'))

    def test_module_loaded(self):
        assert self.module_manager.module_loaded('Parrot')

    def test_calculator_in_module(self):
        assert self.module_manager.has('calculator', 'm3gnet')

    def test_load_calculator(self):
        _ = self.module_manager.get('calculator', 'm3gnet')

    def test_h2_energy_m3gnet_mp_202128_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-pes'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -0.2376336163141, rtol=1e-5)

    def test_h2_gradients_m3gnet_mp_202128_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-pes'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.gradients[0][0] == 0.0
        assert results.gradients[1][0] == 0.0
        assert results.gradients[0][1] == 0.0
        assert results.gradients[1][1] == 0.0
        assert np.isclose(results.gradients[0][2], 0.00733213, rtol=1e-5)
        assert np.isclose(results.gradients[1][2], -0.00733213, rtol=1e-5)

    def test_h2_hessian_m3gnet_mp_202128_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-pes'
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

    def test_h2_charges_m3gnet_mp_202128_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-pes'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.AtomicCharges])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.atomic_charges
        assert len(results.atomic_charges) == 2
        assert np.isclose(results.atomic_charges[0], 0.0, atol=1e-5)
        assert np.isclose(results.atomic_charges[1], 0.0, atol=1e-5)

    def test_h2_bond_order_m3gnet_mp_202128_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-pes'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.BondOrderMatrix])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.bond_orders
        assert results.bond_orders.get_order(0, 1) != 0.0
        assert results.bond_orders.get_order(0, 0) == 0.0
        assert results.bond_orders.get_order(1, 1) == 0.0

    def test_h2_readuct_optimization_m3gnet_mp_202128_pes(self):
        import scine_readuct as readuct

        systems = {
            'guess': self.module_manager.get('calculator', 'm3gnet'),
        }

        systems['guess'].structure = self.h2
        systems['guess'].settings['molecular_charge'] = 0
        systems['guess'].settings['spin_multiplicity'] = 1
        systems['guess'].settings['method'] = 'm3gnet-mp-2021.2.8-pes'

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

    def test_h2_energy_m3gnet_mp_202128_direct_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-direct-pes'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -0.2307380015039, rtol=1e-5)

    def test_h2_gradients_m3gnet_mp_202128_direct_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-direct-pes'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.gradients[0][0] == 0.0
        assert results.gradients[1][0] == 0.0
        assert results.gradients[0][1] == 0.0
        assert results.gradients[1][1] == 0.0
        assert np.isclose(results.gradients[0][2], -0.00352965, rtol=1e-5)
        assert np.isclose(results.gradients[1][2], 0.00352965, rtol=1e-5)

    def test_h2_hessian_m3gnet_mp_202128_direct_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-direct-pes'
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

    def test_h2_charges_m3gnet_mp_202128_direct_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-direct-pes'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.AtomicCharges])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.atomic_charges
        assert len(results.atomic_charges) == 2
        assert np.isclose(results.atomic_charges[0], 0.0, atol=1e-5)
        assert np.isclose(results.atomic_charges[1], 0.0, atol=1e-5)

    def test_h2_bond_order_m3gnet_mp_202128_direct_pes(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['method'] = 'm3gnet-mp-2021.2.8-direct-pes'
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.BondOrderMatrix])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.bond_orders
        assert results.bond_orders.get_order(0, 1) != 0.0
        assert results.bond_orders.get_order(0, 0) == 0.0
        assert results.bond_orders.get_order(1, 1) == 0.0

    def test_h2_readuct_optimization_m3gnet_mp_202128_direct_pes(self):
        import scine_readuct as readuct

        systems = {
            'guess': self.module_manager.get('calculator', 'm3gnet'),
        }

        systems['guess'].structure = self.h2
        systems['guess'].settings['molecular_charge'] = 0
        systems['guess'].settings['spin_multiplicity'] = 1
        systems['guess'].settings['method'] = 'm3gnet-mp-2021.2.8-direct-pes'

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

    def test_ch4_energy(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.ch4
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.isclose(results.energy, -0.8073076594117, rtol=1e-5)

    def test_ch4_gradients(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
        assert calculator is not None
        calculator.structure = self.ch4
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        gradients_ref = np.array([[-0.02133534, 0.03834892, 0.01527303],
                                  [0.05151146, -0.06731552, 0.03169830],
                                  [-0.01742607, 0.03720196, -0.02008254],
                                  [-0.01194220, -0.00736679, -0.01864578],
                                  [-0.00080784, -0.00086856, -0.00824301]])
        assert np.all(np.isclose(results.gradients, gradients_ref, rtol=1e-5))

    def test_ch4_hessian(self):
        calculator = self.module_manager.get('calculator', 'm3gnet')
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
        calculator = self.module_manager.get('calculator', 'm3gnet')
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
        calculator = self.module_manager.get('calculator', 'm3gnet')
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
            'guess': self.module_manager.get('calculator', 'm3gnet'),
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
