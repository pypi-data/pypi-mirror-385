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


class LmlpCalculatorTest(unittest.TestCase):

    module_manager = utils.core.ModuleManager.get_instance()
    module_manager.load_module(ParrotModule())
    h2, _ = utils.io.read(os.path.join(path_test_resources(), 'h2.xyz'))
    brch3cl, _ = utils.io.read(os.path.join(path_test_resources(), 'br-ch3-cl.xyz'))

    def test_module_loaded(self):
        assert self.module_manager.module_loaded('Parrot')

    def test_calculator_in_module(self):
        assert self.module_manager.has('calculator', 'lmlp')

    def test_load_calculator(self):
        _ = self.module_manager.get('calculator', 'lmlp')

    def test_h2_energy(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.energy != 0.0

    def test_h2_gradients(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.gradients[0][0] == 0.0
        assert results.gradients[1][0] == 0.0
        assert results.gradients[0][1] == 0.0
        assert results.gradients[1][1] == 0.0
        assert results.gradients[0][2] != 0.0
        assert results.gradients[1][2] != 0.0

    def test_h2_hessian(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.h2
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

    def test_h2_charges(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.AtomicCharges])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.atomic_charges
        assert len(results.atomic_charges) == 2
        assert np.isclose(results.atomic_charges[0], 0.0, atol=1e-5)
        assert np.isclose(results.atomic_charges[1], 0.0, atol=1e-5)

    def test_h2_bond_order(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.h2
        calculator.settings['molecular_charge'] = 0
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.BondOrderMatrix])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.bond_orders
        assert results.bond_orders.get_order(0, 1) != 0.0
        assert results.bond_orders.get_order(0, 0) == 0.0
        assert results.bond_orders.get_order(1, 1) == 0.0

    def test_h2_readuct_optimization(self):
        import scine_readuct as readuct

        systems = {
            'guess': self.module_manager.get('calculator', 'lmlp'),
        }

        systems['guess'].structure = self.h2
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

    def test_brch3cl_energy(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.brch3cl
        calculator.settings['molecular_charge'] = -1
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Energy])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.energy != 0.0

    def test_brch3cl_gradients(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.brch3cl
        calculator.settings['molecular_charge'] = -1
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Gradients])
        results = calculator.calculate()
        assert results.successful_calculation
        assert np.all(results.gradients[[3, 5], 0] != 0.0)
        assert np.all(results.gradients[3:, 1] != 0.0)
        assert np.all(results.gradients[:, 2] != 0.0)

    def test_brch3cl_hessian(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.brch3cl
        calculator.settings['molecular_charge'] = -1
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.Hessian])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.hessian is not None
        assert np.any(results.hessian.flatten() != 0.0)
        assert results.thermochemistry is not None
        assert results.thermochemistry.overall.gibbs_free_energy != 0.0

    def test_brch3cl_charges(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.brch3cl
        calculator.settings['molecular_charge'] = -1
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.AtomicCharges])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.atomic_charges
        assert len(results.atomic_charges) == 6
        assert np.all(results.atomic_charges != 0.0)

    def test_brch3cl_bond_order(self):
        calculator = self.module_manager.get('calculator', 'lmlp')
        assert calculator is not None
        calculator.structure = self.brch3cl
        calculator.settings['molecular_charge'] = -1
        calculator.settings['spin_multiplicity'] = 1
        calculator.set_required_properties([utils.Property.BondOrderMatrix])
        results = calculator.calculate()
        assert results.successful_calculation
        assert results.bond_orders
        for i in range(3, 6):
            assert results.bond_orders.get_order(1, i) != 0.0
        for i in range(6):
            assert results.bond_orders.get_order(i, i) == 0.0

    def test_brch3cl_readuct_optimization(self):
        import scine_readuct as readuct

        systems = {
            'guess': self.module_manager.get('calculator', 'lmlp'),
        }

        systems['guess'].structure = self.brch3cl
        systems['guess'].settings['molecular_charge'] = -1
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
