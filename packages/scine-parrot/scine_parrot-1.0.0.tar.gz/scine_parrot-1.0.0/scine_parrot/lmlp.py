#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__copyright__ = """ This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Department of Chemistry and Applied Biosciences, Reiher Group.
See LICENSE.txt for details.
"""

####################################################################################################

####################################################################################################

from ast import literal_eval
from copy import deepcopy
from os import environ, path
from pathlib import Path
from types import SimpleNamespace
from typing import Any, List, Tuple
import configparser
import sys
import warnings
import numpy as np
import torch
from numba import jit, NumbaTypeSafetyWarning, typed   # type: ignore
from numpy import pi
from numpy.typing import NDArray
from torch import Tensor


####################################################################################################

####################################################################################################

# decorator for disabled Numba just-in-time compilation
def nojit(func):
    '''
    No Numba just-in-time compilation
    '''
    return func


# Set Numba, NumPy, and PyTorch number of threads
if environ.get('NUMBA_NUM_THREADS') is None:
    environ['NUMBA_NUM_THREADS'] = '1'
if environ.get('OMP_NUM_THREADS') is None:
    environ['OMP_NUM_THREADS'] = '1'
if environ.get('MKL_NUM_THREADS') is None:
    environ['MKL_NUM_THREADS'] = '1'
if environ.get('OPENBLAS_NUM_THREADS') is None:
    environ['OPENBLAS_NUM_THREADS'] = '1'
torch.set_num_interop_threads(1)

# for NUMBA_JIT=0 turn off Numba just-in-time compilation
if environ.get('NUMBA_JIT') == '0':
    ncfjit = nojit

# construct decorators for Numba just-in-time compilation
else:
    assert environ.get('NUMBA_NUM_THREADS') is not None, \
        'ERROR: Environment variable NUMBA_NUM_THREADS is not set.'
    ncfjit = jit(nopython=True, cache=True, fastmath=True)


####################################################################################################

####################################################################################################

class lMLP():
    '''
    Lifelong Machine Learning Potential
    '''

####################################################################################################

    def __init__(self, generalization_setting_file, uncertainty_scaling=2.0,
                 uncertainty_thresholds=(30.0, 60.0, 180.0), active_learning_file=None,
                 active_learning_thresholds=(3.0, 6.0, 18.0), active_learning_max_number=250,
                 active_learning_min_step_difference=5, active_learning_min_atom_distance=0.65):
        '''
        Initialization
        '''
        # get settings
        self.settings = SimpleNamespace(
            generalization_setting_format='lMLP',
            generalization_setting_file=generalization_setting_file,
            generalization_dir=Path(generalization_setting_file).parent,
            uncertainty_scaling=uncertainty_scaling,
            uncertainty_thresholds=uncertainty_thresholds,
            active_learning_file=active_learning_file,
            active_learning_thresholds=active_learning_thresholds,
            active_learning_max_number=active_learning_max_number,
            active_learning_min_step_difference=active_learning_min_step_difference,
            active_learning_min_atom_distance=active_learning_min_atom_distance)

        # define unit conversion factors
        self.Bohr2Angstrom = 0.529177210903   # CODATA 2018
        self.Hartree2eV = 27.211386245988   # CODATA 2018

        # disable debugging functions of PyTorch
        torch.autograd.profiler.emit_nvtx(False)
        torch.autograd.profiler.profile(False)
        torch.autograd.set_detect_anomaly(False)

        # set device used by PyTorch
        self.device = 'cpu'

        # read and set generalization settings
        self.element_types, self.n_descriptors, self.ensemble, self.test_RMSEs = \
            self.read_generalization_setting()
        self.n_element_types = len(self.element_types)

        # define default data type of PyTorch tensors
        self.dtype_torch = self.define_dtype_torch()
        torch.set_default_dtype(self.dtype_torch)

        # initialize descriptor parameters and element energy
        self.descriptor_parameters = []
        self.R_c = 0.0
        self.element_energy = {}

        # define activation function
        self.activation_function = self.define_activation_function()

        # initialize ensemble model
        self.n_ensemble = len(self.ensemble)
        self.model = [None] * self.n_ensemble
        for model_index in range(self.n_ensemble):
            self.define_model(model_index)
            self.settings.generalization_file = path.join(
                self.settings.generalization_dir, self.ensemble[model_index])
            self.read_generalization(model_index)

        # initialize uncertainty prediction
        self.test_RMSEs = np.mean(np.array(self.test_RMSEs), axis=0)

        # create active learning output file
        if self.settings.active_learning_file is not None:
            if self.n_ensemble <= 1:
                sys.exit('ERROR: More than one machine learning potential has to be in the '
                         'ensemble for active learning.')
            Path(self.settings.active_learning_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings.active_learning_file, 'w', encoding='utf-8') as f:
                f.write('')
            self.active_learning_counter = 0
            self.prediction_counter = -1
            self.active_learning_step_difference = -1
            self.R_min = self.settings.active_learning_min_atom_distance
        else:
            self.R_min = -1.0

####################################################################################################

    def predict(self, elements, positions_Bohr, lattice_Bohr=None, atomic_classes=None,
                atomic_charges=None, name=None, calc_forces=True, calc_uncertainty=False):
        '''
        Prediction

        Return: energy_prediction, -forces_prediction, energy_uncertainty, forces_uncertainty
        '''
        # convert units
        positions = positions_Bohr * self.Bohr2Angstrom
        if lattice_Bohr is None:
            lattice = None
        else:
            lattice = lattice_Bohr * self.Bohr2Angstrom

        # check settings
        if calc_uncertainty and self.n_ensemble <= 1:
            sys.exit('ERROR: More than one machine learning potential has to be in the ensemble '
                     'for uncertainty quantification.')

        # get settings
        self.settings.calc_forces = calc_forces
        if self.settings.active_learning_file is not None:
            calc_uncertainty = True

        # get structures
        n_structures = 1
        n = 0
        n_atoms_original = len(elements)
        if len(positions) != n_atoms_original:
            sys.exit('ERROR: The lengths of elements and positions do not match.')
        if lattice is None:
            lattice = np.array([])
        else:
            positions_original = [deepcopy(positions)]
            lattices_original = [deepcopy(lattice)]
        QMMM = False
        if atomic_classes is None:
            atomic_classes = np.ones(n_atoms_original, dtype=int)
            elements_unique = np.unique(elements)
        else:
            if len(atomic_classes) != n_atoms_original:
                sys.exit('ERROR: The lengths of elements and atomic_classes do not match.')
            elements_unique = np.unique(elements[atomic_classes == 1])
            if np.max(atomic_classes) > 1:
                QMMM = True
        if atomic_charges is None:
            atomic_charges = np.zeros(n_atoms_original)
        else:
            if len(atomic_charges) != n_atoms_original:
                sys.exit('ERROR: The lengths of elements and atomic_charges do not match.')

        # check structures
        if not np.all(np.isin(elements_unique, self.element_types)):
            sys.exit('ERROR: The lMLP is not able to represent all given chemical elements.\n'
                     '{0} not all in {1}'.format(np.unique(elements), np.unique(self.element_types)))

        # prepare periodic systems
        if len(lattice) > 0:
            PBC = True
            elements, positions, lattice, atomic_classes, atomic_charges, _, _, n_atoms, \
                reorder_original = self.prepare_periodic_systems(
                    elements, positions, lattice, atomic_classes, atomic_charges, 0.0, [],
                    n_atoms_original)
        else:
            PBC = False
            n_atoms = n_atoms_original
            reorder_original = np.empty(0, dtype=int)

        # create lists of structure properties
        elements = [elements]
        positions = [positions]
        lattices = [lattice]
        atomic_classes = [atomic_classes]
        atomic_charges = [atomic_charges]
        n_atoms = np.array([n_atoms])
        if name is None:
            name = []
        else:
            name = [name]

        # order atoms by atomic type
        if QMMM:
            elements, positions, atomic_classes, atomic_charges, _, n_atoms_sys, reorder = \
                self.atomic_type_ordering(elements, positions, atomic_classes, atomic_charges, [],
                                          n_structures, n_atoms)
        else:
            n_atoms_sys = n_atoms
            reorder = []

        # determine element integer list
        elements_int_sys = self.convert_element_names(elements, n_structures, n_atoms_sys)

        # determine neighbor indices and descriptors and their derivatives as a function of the
        # Cartesian coordinates
        descriptors_torch, descriptor_derivatives_torch, neighbor_indices, \
            descriptor_neighbor_derivatives_torch_env, neighbor_indices_env, active_atoms, \
            n_atoms_active, MM_gradients = self.calculate_descriptors(
                elements_int_sys, positions, lattices, atomic_classes, atomic_charges, n_structures,
                n_atoms, n_atoms_sys, [], R_min=self.R_min)

        # return NaN if minimal interatomic distance is deceeded
        if len(n_atoms_active) <= 0:
            print('WARNING: Minimal interatomic distance is deceeded.\n'
                  'Predictions and uncertainties are set to NaN.\n')
            energy_prediction = np.nan
            energy_uncertainty = np.nan
            if self.settings.calc_forces:
                forces_prediction = np.nan
                forces_uncertainty = np.nan

        # calculate energy and forces of all ensemble members
        else:
            energy_prediction = np.empty(self.n_ensemble)
            if self.settings.calc_forces:
                forces_prediction = np.empty((self.n_ensemble, n_atoms[n], 3))
            for model_index in range(self.n_ensemble):
                energy_prediction_torch, forces_prediction_torch = self.calculate_energy_forces(
                    model_index, n, elements_int_sys, descriptors_torch, descriptor_derivatives_torch,
                    neighbor_indices, n_atoms_sys, descriptor_neighbor_derivatives_torch_env,
                    neighbor_indices_env, n_atoms_active, MM_gradients, create_graph=False)
                energy_prediction[model_index] = float(energy_prediction_torch.cpu().detach().numpy()[0])
                if self.settings.calc_forces:
                    if self.settings.QMMM:
                        forces_prediction[model_index] = np.zeros((n_atoms[n], 3))
                        forces_prediction[model_index][active_atoms[n]] = \
                            forces_prediction_torch.cpu().detach().numpy().astype(float)
                    else:
                        forces_prediction[model_index] = \
                            forces_prediction_torch.cpu().detach().numpy().astype(float)

            # calculate ensemble prediction and uncertainty of energy and forces including
            # element-specific atomic energies
            if calc_uncertainty:
                energy_uncertainty = max(
                    self.test_RMSEs[0] * n_atoms_sys[n], self.settings.uncertainty_scaling
                    * np.std(energy_prediction, ddof=1))
            else:
                energy_uncertainty = 0.0
            energy_prediction = np.mean(energy_prediction) + np.sum(np.array([
                self.element_energy[ele] for ele in elements[n][:n_atoms_sys[n]]]))
            if self.settings.calc_forces:
                if calc_uncertainty:
                    forces_uncertainty = self.settings.uncertainty_scaling * np.std(
                        forces_prediction, ddof=1, axis=0)
                    forces_uncertainty[:n_atoms_sys[n]][forces_uncertainty[
                        :n_atoms_sys[n]] < self.test_RMSEs[1]] = self.test_RMSEs[1]
                    if self.settings.QMMM:
                        active_atoms_env = np.arange(n_atoms[n])[active_atoms[n][n_atoms_sys[n]:]]
                        for i in range(3):
                            forces_uncertainty[:, i][active_atoms_env[forces_uncertainty[:, i][
                                active_atoms_env] < self.test_RMSEs[2]]] = self.test_RMSEs[2]
                forces_prediction = np.mean(forces_prediction, axis=0)

            # get bad represented structures for active learning
            if calc_uncertainty:
                energy_uncertainty_per_atom = energy_uncertainty / n_atoms_sys[n]
                forces_uncertainty_max = 0.0
                forces_uncertainty_max_env = 0.0
                if self.settings.calc_forces:
                    forces_uncertainty_max = np.max(forces_uncertainty[:n_atoms_sys[n]])
                    if self.settings.QMMM:
                        forces_uncertainty_max_env = np.max(forces_uncertainty[n_atoms_sys[n]:])
            retrain = False
            if self.settings.active_learning_file is not None:
                self.prediction_counter += 1
                self.active_learning_step_difference += 1
                if self.active_learning_step_difference >= self.settings.active_learning_min_step_difference:
                    if energy_uncertainty_per_atom > (
                            self.settings.active_learning_thresholds[0] * self.test_RMSEs[0]):
                        retrain = True
                    if self.settings.calc_forces:
                        if forces_uncertainty_max > (
                                self.settings.active_learning_thresholds[1] * self.test_RMSEs[1]):
                            retrain = True
                        if self.settings.QMMM:
                            if forces_uncertainty_max_env > (
                                    self.settings.active_learning_thresholds[2] * self.test_RMSEs[2]):
                                retrain = True

            # get energy of original atoms
            n_images = n_atoms[n] / n_atoms_original
            energy_prediction /= n_images
            if calc_uncertainty:
                energy_uncertainty /= n_images

            # reorder forces and get original atoms
            if self.settings.calc_forces:
                if QMMM:
                    forces_prediction = forces_prediction[reorder[n]]
                if PBC:
                    forces_prediction = forces_prediction[reorder_original]
                if calc_uncertainty:
                    if QMMM:
                        forces_uncertainty = forces_uncertainty[reorder[n]]
                    if PBC:
                        forces_uncertainty = forces_uncertainty[reorder_original]

            # write bad represented structures to a file for active learning
            if retrain:
                self.active_learning_step_difference = 0
                self.active_learning_counter += 1
                if QMMM:
                    elements[n] = elements[n][reorder[n]]
                    positions[n] = positions[n][reorder[n]]
                    atomic_classes[n] = atomic_classes[n][reorder[n]]
                    atomic_charges[n] = atomic_charges[n][reorder[n]]
                if PBC:
                    elements[n] = elements[n][reorder_original]
                    positions = positions_original
                    lattices = lattices_original
                    atomic_classes[n] = atomic_classes[n][reorder_original]
                    atomic_charges[n] = atomic_charges[n][reorder_original]
                    n_atoms[n] = n_atoms_original
                if self.settings.calc_forces:
                    if self.settings.QMMM:
                        uncertainty = [[energy_uncertainty_per_atom, forces_uncertainty_max,
                                       forces_uncertainty_max_env]]
                    else:
                        uncertainty = [[energy_uncertainty_per_atom, forces_uncertainty_max]]
                else:
                    uncertainty = [[energy_uncertainty_per_atom]]
                    forces_prediction = np.zeros((n_atoms[n], 3))
                self.write_inputdata(
                    self.settings.active_learning_file, elements, positions, lattices,
                    atomic_classes, atomic_charges, [energy_prediction], [forces_prediction],
                    n_structures, n_atoms, [np.arange(n_atoms[n])], name=name,
                    uncertainty=uncertainty, counter=self.prediction_counter, mode='a')

            # return NaN if uncertainty thresholds are exceeded or maximal number of active learning
            # structures is reached
            if calc_uncertainty:
                stop = False
                if energy_uncertainty_per_atom > (
                        self.settings.uncertainty_thresholds[0] * self.test_RMSEs[0]):
                    print('WARNING: Energy uncertainty threshold is exceeded.')
                    stop = True
                if self.settings.calc_forces:
                    if forces_uncertainty_max > (
                            self.settings.uncertainty_thresholds[1] * self.test_RMSEs[1]):
                        print('WARNING: Forces uncertainty threshold is exceeded.')
                        stop = True
                    if self.settings.QMMM:
                        if forces_uncertainty_max_env > (
                                self.settings.uncertainty_thresholds[2] * self.test_RMSEs[2]):
                            print('WARNING: Environment forces uncertainty threshold is exceeded.')
                            stop = True
                if retrain:
                    if self.active_learning_counter >= self.settings.active_learning_max_number:
                        print('WARNING: Maximal number of active learning structures is reached.')
                        stop = True
                if stop:
                    print('Predictions and uncertainties are set to NaN.\n')
                    energy_prediction = np.nan
                    energy_uncertainty = np.nan
                    if self.settings.calc_forces:
                        forces_prediction = np.nan
                        forces_uncertainty = np.nan

        # reconvert units
        energy_prediction /= self.Hartree2eV
        if calc_uncertainty:
            energy_uncertainty /= self.Hartree2eV
        if self.settings.calc_forces:
            forces_prediction *= self.Bohr2Angstrom / self.Hartree2eV
            if calc_uncertainty:
                forces_uncertainty *= self.Bohr2Angstrom / self.Hartree2eV

        # return requested properties
        if self.settings.calc_forces:
            if calc_uncertainty:
                return energy_prediction, -forces_prediction, energy_uncertainty, forces_uncertainty
            return energy_prediction, -forces_prediction
        if calc_uncertainty:
            return energy_prediction, energy_uncertainty
        return energy_prediction

####################################################################################################

    def define_dtype_torch(self):
        '''
        Implementation: float, double

        Return: dtype_torch
        '''
        # implemented torch dtypes
        dtype_torch_list = ['float', 'double']

        # torch dtype float
        if self.settings.dtype_torch == 'float':
            dtype_torch = torch.float

        # torch dtype double
        elif self.settings.dtype_torch == 'double':
            dtype_torch = torch.double

        # not implemented torch dtype
        else:
            print('ERROR: Using the data type {0} is not yet implemented for PyTorch tensors.'
                  .format(self.settings.dtype_torch),
                  '\nPlease use one of the following data types:')
            for dty_tor in dtype_torch_list:
                print('{0}'.format(dty_tor))
            sys.exit()

        return dtype_torch

####################################################################################################

    def read_generalization_setting(self):
        '''
        Implementation: lMLP

        Modify: generalization_format, model_type, descriptor_type, descriptor_radial_type,
                descriptor_angular_type, descriptor_scaling_type, scale_shift_layer,
                n_neurons_hidden_layers, activation_function_type, dtype_torch, QMMM,
                MM_atomic_charge_max

        Return: element_types, n_descriptors, ensemble, test_RMSEs
        '''
        # implemented file formats
        generalization_setting_format_list = ['lMLP']

        # check existance of file
        if not path.isfile(self.settings.generalization_setting_file):
            sys.exit('ERROR: Generalization setting file {0} does not exist.'.format(
                self.settings.generalization_setting_file))

        # read file format lMLP
        if self.settings.generalization_setting_format == 'lMLP':
            element_types, n_descriptors, ensemble, test_RMSEs = self.read_settings()

        # not implemented file format
        else:
            print('ERROR: Generalization setting format {0} is not yet implemented.'
                  .format(self.settings.generalization_setting_format),
                  '\nPlease use one of the following formats:')
            for gen_set_format in generalization_setting_format_list:
                print('{0}'.format(gen_set_format))
            sys.exit()

        return element_types, n_descriptors, ensemble, test_RMSEs

####################################################################################################

    def read_settings(self):
        '''
        Modify: generalization_format, model_type, descriptor_type, descriptor_radial_type,
                descriptor_angular_type, descriptor_scaling_type, scale_shift_layer,
                n_neurons_hidden_layers, activation_function_type, dtype_torch, QMMM,
                MM_atomic_charge_max

        Return: element_types, n_descriptors, ensemble, test_RMSEs
        '''
        # initialize configparser
        config = configparser.ConfigParser()
        files = config.read(self.settings.generalization_setting_file)

        # check generalization setting file
        if len(files) != 1:
            sys.exit('ERROR: Generalization setting file {0} does not exist or is broken.'.format(
                self.settings.generalization_setting_file))
        generalization_settings = config['settings']

        # get generalization settings
        self.settings.generalization_format = generalization_settings['generalization_format']
        ensemble = literal_eval(generalization_settings['ensemble'])
        test_RMSEs = literal_eval(generalization_settings['test_RMSEs'])
        self.settings.model_type = generalization_settings['model_type']
        element_types = np.array(literal_eval(generalization_settings['element_types']))
        self.settings.descriptor_type = generalization_settings['descriptor_type']
        self.settings.descriptor_radial_type = generalization_settings['descriptor_radial_type']
        self.settings.descriptor_angular_type = generalization_settings['descriptor_angular_type']
        self.settings.descriptor_scaling_type = generalization_settings['descriptor_scaling_type']
        n_descriptors = literal_eval(generalization_settings['n_descriptors'])
        self.settings.scale_shift_layer = literal_eval(generalization_settings['scale_shift_layer'])
        self.settings.n_neurons_hidden_layers = literal_eval(generalization_settings['n_neurons_hidden_layers'])
        self.settings.activation_function_type = generalization_settings['activation_function_type']
        self.settings.dtype_torch = generalization_settings['dtype_torch']
        self.settings.QMMM = literal_eval(generalization_settings['QMMM'])
        self.settings.MM_atomic_charge_max = literal_eval(generalization_settings['MM_atomic_charge_max'])

        return element_types, n_descriptors, ensemble, test_RMSEs

####################################################################################################

    def prepare_periodic_systems(self, elements, positions, lattice, atomic_classes, atomic_charges,
                                 energy, forces, n_atoms):
        '''
        Return: elements, positions, lattice, atomic_classes, atomic_charges, energy, forces,
                n_atoms, reorder
        '''
        # order system and environment atoms
        if self.settings.QMMM:
            order = np.arange(n_atoms)[atomic_classes == 1]
            n_atoms_sys = len(order)
            order = np.concatenate((order, np.arange(n_atoms)[atomic_classes == 2]))
            elements = elements[order]
            positions = positions[order]
            atomic_classes = atomic_classes[order]
            atomic_charges = atomic_charges[order]
            if len(forces) > 0:
                forces = forces[order]
            reorder = np.argsort(order)
        else:
            n_atoms_sys = n_atoms
            reorder = np.arange(n_atoms)

        # align center of system atoms and center of cell for QMMM, wrap atoms into original cell,
        # determine if periodic boundary conditions are required, and expand cell if its heights are
        # smaller than the cutoff radius
        positions, lattice, pbc_required, n_images_tot = prepare_periodic_cell(
            positions, lattice, n_atoms, n_atoms_sys, self.R_c)

        # expand periodic system if its heights are smaller than the cutoff radius
        if pbc_required:
            if n_images_tot > 1:
                elements = np.tile(elements, n_images_tot)
                atomic_classes = np.tile(atomic_classes, n_images_tot)
                atomic_charges = np.tile(atomic_charges, n_images_tot)
                energy *= n_images_tot
                if len(forces) > 0:
                    forces = np.tile(forces, (n_images_tot, 1))
                n_atoms *= n_images_tot

        # remove lattice if periodic boundary conditions are not required
        else:
            lattice = np.array([])

        return elements, positions, lattice, atomic_classes, atomic_charges, energy, forces, \
            n_atoms, reorder

####################################################################################################

    def atomic_type_ordering(self, elements, positions, atomic_classes, atomic_charges, forces,
                             n_structures, n_atoms):
        '''
        Return: elements, positions, atomic_classes, atomic_charges, forces, n_atoms_sys, reorder
        '''
        # order elements, positions, atomic_classes, atomic_charges, and forces by atomic class
        n_forces = len(forces)
        n_atoms_sys = np.empty(n_structures, dtype=int)
        reorder = []
        for n in range(n_structures):
            order = np.arange(n_atoms[n])[atomic_classes[n] == 1]
            n_atoms_sys[n] = len(order)
            order = np.concatenate((order, np.arange(n_atoms[n])[atomic_classes[n] == 2]))
            elements[n] = elements[n][order]
            positions[n] = positions[n][order]
            atomic_classes[n] = atomic_classes[n][order]
            atomic_charges[n] = atomic_charges[n][order]
            if n_forces:
                forces[n] = forces[n][order]
            reorder.append(np.argsort(order))

        return elements, positions, atomic_classes, atomic_charges, forces, n_atoms_sys, reorder

####################################################################################################

    def convert_element_names(self, elements, n_structures, n_atoms_sys):
        '''
        Return: elements_int_sys
        '''
        # initialize list
        elements_int_sys = []

        # create integer arrays for the elements of every structure
        for n in range(n_structures):
            elements_int_sys.append(-np.ones(n_atoms_sys[n], dtype=int))
            # set correct indices for all element types
            for i in range(self.n_element_types):
                elements_int_sys[n][elements[n][:n_atoms_sys[n]] == self.element_types[i]] = i
            if np.any(elements_int_sys[n] < 0):
                sys.exit('ERROR: Not all element types are spezified in the settings.\n'
                         'All specifications: {0}, current structure: {1}.'
                         .format(self.element_types, np.unique(elements[n][:n_atoms_sys[n]])))

        return elements_int_sys

####################################################################################################

    def calculate_descriptors(self, elements_int_sys, positions, lattices, atomic_classes,
                              atomic_charges, n_structures, n_atoms, n_atoms_sys, name, R_min=-1.0):
        '''
        Limitation: All elements will have the same set of descriptors

        Implementation: ACSF, eeACSF

        Return: descriptors_torch, descriptor_derivatives_torch, neighbor_indices,
                descriptor_neighbor_derivatives_torch_env, neighbor_indices_env, active_atoms,
                n_atoms_active, MM_gradients
        '''
        # implemented descriptor types
        descriptor_type_list = ['ACSF', 'eeACSF']

        # calculate ACSFs or eeACSFs
        if self.settings.descriptor_type in ('ACSF', 'eeACSF'):
            descriptors_torch, descriptor_derivatives_torch, neighbor_indices, \
                descriptor_neighbor_derivatives_torch_env, neighbor_indices_env, active_atoms, \
                n_atoms_active, MM_gradients = self.calculate_symmetry_function(
                    elements_int_sys, positions, lattices, atomic_classes, atomic_charges, n_structures,
                    n_atoms, n_atoms_sys, name, R_min)

        # not implemented descriptor type
        else:
            print('ERROR: Calculating descriptor type {0} is not yet implemented.'
                  .format(self.settings.descriptor_type),
                  '\nPlease use one of the following types:')
            for des_type in descriptor_type_list:
                print('{0}'.format(des_type))
            sys.exit()

        return descriptors_torch, descriptor_derivatives_torch, neighbor_indices, \
            descriptor_neighbor_derivatives_torch_env, neighbor_indices_env, active_atoms, \
            n_atoms_active, MM_gradients

####################################################################################################

    def calculate_symmetry_function(self, elements_int_sys, positions, lattices, atomic_classes,
                                    atomic_charges, n_structures, n_atoms, n_atoms_sys, _, R_min):
        '''
        Implementation: Radial types: bump, Gaussian-bump, Gaussian-cosine
                        Angular types: bump, cosine, cosine_integer
                        Scaling types: cube root-scaled-shifted, linear, square root

        Return: descriptors_torch, [descriptor_i_derivatives_torch,
                descriptor_neighbor_derivatives_torch], neighbor_indices,
                descriptor_neighbor_derivatives_torch_env, neighbor_indices_env, active_atoms,
                n_atoms_active, MM_gradients
        '''
        # implemented descriptor radial types
        descriptor_radial_type_list = ['bump', 'gaussian_bump', 'gaussian_cos']
        # implemented descriptor angular types
        descriptor_angular_type_list = ['bump', 'cos', 'cos_int']
        # implemented descriptor radial types
        descriptor_scaling_type_list = ['crss', 'linear', 'sqrt']

        # get bump radial function index
        if self.settings.descriptor_radial_type == 'bump':
            rad_func_index = 0
        # get Gaussian-bump radial function index
        elif self.settings.descriptor_radial_type == 'gaussian_bump':
            rad_func_index = 1
        # get Gaussian-cosine radial function index
        elif self.settings.descriptor_radial_type == 'gaussian_cos':
            rad_func_index = 2
        # not implemented descriptor radial type
        else:
            print('ERROR: Calculating descriptor radial type {0} is not yet implemented.'
                  .format(self.settings.descriptor_radial_type),
                  '\nPlease use one of the following types:')
            for des_rad_type in descriptor_radial_type_list:
                print('{0}'.format(des_rad_type))
            sys.exit()

        # get bump angular function index
        if self.settings.descriptor_angular_type == 'bump':
            ang_func_index = 0
        # get cosine angular function index
        elif self.settings.descriptor_angular_type == 'cos':
            ang_func_index = 1
        # get cosine integer angular function index
        elif self.settings.descriptor_angular_type == 'cos_int':
            ang_func_index = 2
        # not implemented descriptor angular type
        else:
            print('ERROR: Calculating descriptor angular type {0} is not yet implemented.'
                  .format(self.settings.descriptor_angular_type),
                  '\nPlease use one of the following types:')
            for des_ang_type in descriptor_angular_type_list:
                print('{0}'.format(des_ang_type))
            sys.exit()

        # check descriptor scaling type for QM/MM data
        if self.settings.QMMM and self.settings.descriptor_scaling_type != 'linear':
            sys.exit('ERROR: QM/MM data require descriptor scaling type linear.')
        # get cube root-scaled-shifted scaling function index
        if self.settings.descriptor_scaling_type == 'crss':
            scale_func_index = 0
        # get linear scaling function index
        elif self.settings.descriptor_scaling_type == 'linear':
            scale_func_index = 1
        # get square root scaling function index
        elif self.settings.descriptor_scaling_type == 'sqrt':
            scale_func_index = 2
        # not implemented descriptor scaling type
        else:
            print('ERROR: Calculating descriptor scaling type {0} is not yet implemented.'
                  .format(self.settings.descriptor_scaling_type),
                  '\nPlease use one of the following types:')
            for des_sca_type in descriptor_scaling_type_list:
                print('{0}'.format(des_sca_type))
            sys.exit()

        # determine number of radial and angular parameters
        n_parameters_ang = np.sum(np.array(
            [self.descriptor_parameters[i][0] for i in range(self.n_descriptors)])) - self.n_descriptors
        n_parameters_rad = self.n_descriptors - n_parameters_ang
        parameters_rad = np.array(self.descriptor_parameters[:n_parameters_rad])
        # get element-dependent radial and angular function index
        if self.settings.descriptor_type == 'eeACSF':
            element_types_rad = np.array([], dtype=int)
            if self.settings.QMMM:
                elem_func_index = 2
            else:
                elem_func_index = 0
        elif self.settings.descriptor_type == 'ACSF':
            element_types_rad = np.tile(
                np.arange(self.n_element_types), n_parameters_rad // self.n_element_types)
            if self.settings.QMMM:
                sys.exit('ERROR: QM/MM reference data cannot be represented by ACSFs.\n'
                         'Please use the descriptor type eeACSFs.')
            else:
                elem_func_index = 1

        # radial and angular symmetry functions
        if n_parameters_ang > 0:
            parameters_ang = np.array(self.descriptor_parameters[n_parameters_rad:])
            n_element_types_ang = 0
            element_types_ang = np.array([], dtype=int)
            H_parameters_rad = np.array([], dtype=int)
            H_parameters_ang = np.array([], dtype=int)
            H_parameters_rad_scale = np.array([])
            H_parameters_ang_scale = np.array([])
            n_H_parameters = 0
            if self.settings.descriptor_type == 'ACSF':
                # determine angular parameters
                n_element_types_ang = np.sum(np.arange(1, self.n_element_types + 1))
                element_types_ang = np.tile(np.array(
                    [1000 * i + j for i in range(self.n_element_types)
                     for j in range(i, self.n_element_types)]), n_parameters_ang // n_element_types_ang)
                # slice parameters array
                H_type_jk = np.array([], dtype=int)
                eta_ij = parameters_rad[:, 1]
                eta_ijk = parameters_ang[:, 1]
                lambda_ijk = parameters_ang[:, 2]
                zeta_ijk = parameters_ang[:, 3]
                xi_ijk = parameters_ang[:, 4]
            elif self.settings.descriptor_type == 'eeACSF':
                # slice parameters array
                H_type_j = parameters_rad[:, 1].astype(int)
                H_type_jk = parameters_ang[:, 1].astype(int)
                eta_ij = parameters_rad[:, 2]
                eta_ijk = parameters_ang[:, 2]
                lambda_ijk = parameters_ang[:, 3]
                zeta_ijk = parameters_ang[:, 4]
                xi_ijk = parameters_ang[:, 5]
                # determine H parameters
                H_parameters_rad, H_parameters_ang, H_parameters_rad_scale, H_parameters_ang_scale, \
                    n_H_parameters = self.get_H_parameters(H_type_j, H_type_jk)
            if self.settings.QMMM:
                # slice parameters array
                I_type_j = parameters_rad[:, 3].astype(int)
                I_type_jk = parameters_ang[:, 6].astype(int)
                # check if H and I types are compatible
                if np.any(np.logical_and(np.greater(H_type_jk, n_H_parameters), np.greater(I_type_jk, 2))):
                    sys.exit('ERROR: Angular symmetry function subtypes cannot be larger than '
                             '{0} for QM/MM subtypes larger than 2.'.format(n_H_parameters))
                # determine I parameters
                n_parameters_rad_env = len(np.arange(n_parameters_rad)[I_type_j > 0])
                n_parameters_ang_env = len(np.arange(n_parameters_ang)[I_type_jk > 0])
                MM_gradients = list(np.arange(self.n_descriptors)[
                    np.concatenate((I_type_j > 0, I_type_jk > 0))])
            else:
                # slice parameters array
                I_type_j = np.array([], dtype=int)
                I_type_jk = np.array([], dtype=int)
                # determine I parameters
                n_parameters_rad_env = 0
                n_parameters_ang_env = 0
                MM_gradients = []

            # calculate symmetry function values and derivatives
            descriptors_torch = []
            descriptor_i_derivatives_torch = []
            descriptor_neighbor_derivatives_torch = []
            neighbor_indices = []
            descriptor_neighbor_derivatives_torch_env = []
            neighbor_indices_env = []
            active_atoms = []
            n_atoms_active = []
            for n in range(n_structures):
                # determine interatomic distances and angles for each atom within the cutoff sphere
                neighbor_index, ij_0, ij_1, ij_2, ij_3, ij_4, ijk_0, ijk_1, ijk_2, ijk_3, ijk_4, \
                    ijk_5, ijk_6, ijk_7, ijk_8, ijk_9, ijk_10, ijk_11, ijk_12, active_atom, \
                    neighbor_index_env = self.calculate_atomic_environments(
                        elements_int_sys[n], positions[n], lattices[n], atomic_classes[n],
                        atomic_charges[n], n_atoms[n], n_atoms_sys[n], R_min,
                        calc_derivatives=self.settings.calc_forces)
                if len(active_atom) <= 0:
                    return [], [], [], [], [], [], np.array([]), []
                active_atoms.append(active_atom)
                n_atoms_active.append(len(active_atom))
                neighbor_index_sys = [neighbor_index[i][neighbor_index[i] % n_atoms[n] < n_atoms_sys[n]]
                                      for i in range(len(neighbor_index))]
                neighbor_indices.append([i % n_atoms[n] for i in neighbor_index_sys])
                descriptor_i_derivatives_torch.append([])
                descriptor_neighbor_derivatives_torch.append([])
                neighbor_indices_env.append([i % n_atoms_sys[n] for i in neighbor_index_env])
                descriptor_neighbor_derivatives_torch_env.append([])
                # calculate symmetry function value and derivative contributions
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=NumbaTypeSafetyWarning)
                    descriptor, descriptor_i_derivative, descriptor_neighbor_derivative, \
                        descriptor_neighbor_derivative_env = calc_descriptor_derivative(
                            ij_0, ij_1, ij_2, ij_3, ij_4, ijk_0, ijk_1, ijk_2, ijk_3, ijk_4, ijk_5,
                            ijk_6, ijk_7, ijk_8, ijk_9, ijk_10, ijk_11, ijk_12, neighbor_index,
                            n_atoms[n], n_atoms_sys[n], self.n_descriptors, elem_func_index,
                            rad_func_index, ang_func_index, scale_func_index, self.R_c, eta_ij,
                            H_parameters_rad, H_parameters_rad_scale, n_parameters_rad,
                            element_types_rad, eta_ijk, lambda_ijk, zeta_ijk, xi_ijk,
                            H_parameters_ang, H_parameters_ang_scale, n_parameters_ang, H_type_jk,
                            n_H_parameters, element_types_ang, self.settings.calc_forces,
                            self.settings.QMMM, active_atom, n_atoms_active[n], neighbor_index_env,
                            I_type_j, n_parameters_rad_env, I_type_jk, n_parameters_ang_env,
                            self.settings.MM_atomic_charge_max)
                # compile symmetry function values
                descriptors_torch.append(torch.tensor(np.array(descriptor), requires_grad=True,
                                                      dtype=self.dtype_torch))
                if self.settings.calc_forces:
                    for i in range(n_atoms_sys[n]):
                        # compile symmetry function derivatives with respect to the central atom i
                        descriptor_i_derivatives_torch[-1].append(torch.tensor(
                            descriptor_i_derivative[i], dtype=self.dtype_torch))
                        # compile symmetry function derivatives with respect to neighbor atoms of atom i
                        descriptor_neighbor_derivatives_torch[-1].append(torch.tensor(
                            descriptor_neighbor_derivative[i], dtype=self.dtype_torch))
                    # compile symmetry function derivatives with respect to neighbor active environment
                    # atoms of atom i
                    if self.settings.QMMM:
                        for i in range(n_atoms_active[n] - n_atoms_sys[n]):
                            descriptor_neighbor_derivatives_torch_env[-1].append(torch.tensor(
                                descriptor_neighbor_derivative_env[i], dtype=self.dtype_torch))

        # only radial symmetry functions
        else:
            H_parameters_rad = np.array([], dtype=int)
            H_parameters_rad_scale = np.array([])
            if self.settings.descriptor_type == 'ACSF':
                # slice parameter arrays
                eta_ij = parameters_rad[:, 1]
            elif self.settings.descriptor_type == 'eeACSF':
                # slice parameter arrays
                H_type_j = parameters_rad[:, 1].astype(int)
                eta_ij = parameters_rad[:, 2]
                # determine H parameters
                H_parameters_rad, H_parameters_ang, H_parameters_rad_scale, H_parameters_ang_scale, \
                    n_H_parameters = self.get_H_parameters(H_type_j, np.array([], dtype=int))
            if self.settings.QMMM:
                # slice parameters array
                I_type_j = parameters_rad[:, 3].astype(int)
                # determine I parameters
                n_parameters_rad_env = len(np.arange(n_parameters_rad)[I_type_j > 0])
                MM_gradients = list(np.arange(self.n_descriptors)[I_type_j > 0])
            else:
                # slice parameters array
                I_type_j = np.array([], dtype=int)
                # determine I parameters
                n_parameters_rad_env = 0
                MM_gradients = []

            # calculate symmetry function values and derivatives
            descriptors_torch = []
            descriptor_i_derivatives_torch = []
            descriptor_neighbor_derivatives_torch = []
            neighbor_indices = []
            descriptor_neighbor_derivatives_torch_env = []
            neighbor_indices_env = []
            active_atoms = []
            n_atoms_active = []
            for n in range(n_structures):
                # determine interatomic distances for each atom within the cutoff sphere
                neighbor_index, ij_0, ij_1, ij_2, ij_3, ij_4, ijk_0, ijk_1, ijk_2, ijk_3, ijk_4, \
                    ijk_5, ijk_6, ijk_7, ijk_8, ijk_9, ijk_10, ijk_11, ijk_12, active_atom, \
                    neighbor_index_env = self.calculate_atomic_environments(
                        elements_int_sys[n], positions[n], lattices[n], atomic_classes[n],
                        atomic_charges[n], n_atoms[n], n_atoms_sys[n], R_min,
                        calc_derivatives=self.settings.calc_forces, angular=False)
                if len(active_atom) <= 0:
                    return [], [], [], [], [], [], np.array([]), []
                active_atoms.append(active_atom)
                n_atoms_active.append(len(active_atom))
                neighbor_index_sys = [neighbor_index[i][neighbor_index[i] % n_atoms[n] < n_atoms_sys[n]]
                                      for i in range(len(neighbor_index))]
                neighbor_indices.append([i % n_atoms[n] for i in neighbor_index_sys])
                descriptor_i_derivatives_torch.append([])
                descriptor_neighbor_derivatives_torch.append([])
                neighbor_indices_env.append([i % n_atoms_sys[n] for i in neighbor_index_env])
                descriptor_neighbor_derivatives_torch_env.append([])
                # calculate symmetry function value and derivative contributions
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=NumbaTypeSafetyWarning)
                    descriptor, descriptor_i_derivative, descriptor_neighbor_derivative, \
                        descriptor_neighbor_derivative_env = calc_descriptor_derivative_radial(
                            ij_0, ij_1, ij_2, ij_3, ij_4, neighbor_index, n_atoms[n],
                            n_atoms_sys[n], self.n_descriptors, elem_func_index, rad_func_index,
                            scale_func_index, self.R_c, eta_ij, H_parameters_rad,
                            H_parameters_rad_scale, n_parameters_rad, element_types_rad,
                            self.settings.calc_forces, self.settings.QMMM, active_atom,
                            n_atoms_active[n], neighbor_index_env, I_type_j, n_parameters_rad_env,
                            self.settings.MM_atomic_charge_max)
                # compile symmetry function values
                descriptors_torch.append(torch.tensor(np.array(descriptor), requires_grad=True,
                                                      dtype=self.dtype_torch))
                if self.settings.calc_forces:
                    for i in range(n_atoms_sys[n]):
                        # compile symmetry function derivatives with respect to the central atom i
                        descriptor_i_derivatives_torch[-1].append(torch.tensor(
                            descriptor_i_derivative[i], dtype=self.dtype_torch))
                        # compile symmetry function derivatives with respect to neighbor atoms of atom i
                        descriptor_neighbor_derivatives_torch[-1].append(torch.tensor(
                            descriptor_neighbor_derivative[i], dtype=self.dtype_torch))
                    # compile symmetry function derivatives with respect to neighbor active environment
                    # atoms of atom i
                    if self.settings.QMMM:
                        for i in range(n_atoms_active[n] - n_atoms_sys[n]):
                            descriptor_neighbor_derivatives_torch_env[-1].append(torch.tensor(
                                descriptor_neighbor_derivative_env[i], dtype=self.dtype_torch))

        # convert number of active atoms from list to NumPy array
        n_atoms_active = np.array(n_atoms_active)

        return descriptors_torch, [descriptor_i_derivatives_torch, descriptor_neighbor_derivatives_torch], \
            neighbor_indices, descriptor_neighbor_derivatives_torch_env, neighbor_indices_env, \
            active_atoms, n_atoms_active, MM_gradients

####################################################################################################

    def calculate_atomic_environments(self, elements_int_sys, positions, lattice, atomic_classes,
                                      atomic_charges, n_atoms, n_atoms_sys, R_min,
                                      calc_derivatives=True, angular=True):
        '''
        Output format: ij_list: [ [elements_int_j], [R_ij], [dR_ij__dalpha_i_] ]_atoms
                                (For each atom there are three lists containing neighboring element
                                integers j, distances R_ij, and their derivatives dR_ij_/dalpha_i_,
                                respectively.)
                       ijk_list: [ [elements_int_j], [elements_int_k], [R_ij], [R_ik],
                                 [dR_ij__dalpha_i_], [dR_ik__dalpha_i_], [cos_theta_ijk],
                                 [dcos_theta_ijk__dalpha_] ]_atoms
                                 (For each atom there are eight lists containing neighboring element
                                 integers j and k, distances R_ij and R_ik, their derivatives
                                 dR_ij_/dalpha_i_ and dR_ik_/dalpha_i_, angles cos(theta_ijk), and
                                 their derivatives dcos(theta_ijk)_/dalpha_i,j,k_, respectively.)

                       dR_ij__dalpha_i_: [dR_ij_dx_i, dR_ij_dy_i, dR_ij_dz_i]
                       dcos_theta_ijk__dalpha_: [dct_dx_i, dct_dy_i, dct_dz_i, dct_dx_j, dct_dy_j,
                                                dct_dz_j, dct_dx_k, dct_dy_k, dct_dz_k]

        Hint: dR_ij__dalpha_j_ = -dR_ij__dalpha_i_

        Return: neighbor_index, ij_0, ij_1, ij_2, ij_3, ij_4, ijk_0, ijk_1, ijk_2, ijk_3, ijk_4,
                ijk_5, ijk_6, ijk_7, ijk_8, ijk_9, ijk_10, ijk_11, ijk_12, active_atoms,
                neighbor_index_env
        '''
        # initialize lists
        neighbor_index = typed.List()
        ij_0 = typed.List()
        ij_1 = typed.List()
        ij_2 = typed.List()
        ij_3 = typed.List()
        ij_4 = typed.List()
        ijk_0 = typed.List()
        ijk_1 = typed.List()
        ijk_2 = typed.List()
        ijk_3 = typed.List()
        ijk_4 = typed.List()
        ijk_5 = typed.List()
        ijk_6 = typed.List()
        ijk_7 = typed.List()
        ijk_8 = typed.List()
        ijk_9 = typed.List()
        ijk_10 = typed.List()
        ijk_11 = typed.List()
        ijk_12 = typed.List()

        # handle periodic systems
        if len(lattice) > 0:
            # get adjacent periodic images
            positions_all = get_periodic_images(positions, lattice, n_atoms)
            indices = np.arange(27 * n_atoms)
        # handle non-periodic systems
        else:
            positions_all = positions
            indices = np.arange(n_atoms)

        # determine neighbor indices lists and pair and triple properties inside the cutoff sphere
        # for each atom
        for i in range(n_atoms_sys):
            # pair properties
            # calculate distance vectors and values
            R_ij_ = positions_all - positions[i]
            R_ij = np.sqrt((R_ij_**2).sum(axis=1))
            # determine neighbor atoms inside cutoff sphere
            neighbors = np.less(R_ij, self.R_c)
            neighbors[i] = False
            # extract and sort properties for neighbor atoms
            neighbor_index.append(indices[neighbors])
            order = np.argsort(neighbor_index[-1] % n_atoms)
            neighbor_index[-1] = neighbor_index[-1][order]
            R_ij_ = R_ij_[neighbors][order]
            R_ij = R_ij[neighbors][order]
            # check minimal interatomic distance
            if R_min > 0.0:
                if len(R_ij) > 0:
                    if not np.min(R_ij) >= R_min:
                        return typed.List(), typed.List(), typed.List(), typed.List(), \
                            typed.List(), typed.List(), typed.List(), typed.List(), typed.List(), \
                            typed.List(), typed.List(), typed.List(), typed.List(), typed.List(), \
                            typed.List(), typed.List(), typed.List(), typed.List(), typed.List(), \
                            np.array([]), typed.List()
            # calculate derivatives of R_ij
            dR_ij__dalpha_i_ = -(R_ij_.T / R_ij).T
            # extract properties for QM/MM reference data
            if self.settings.QMMM:
                neighbor_index_sys = neighbor_index[-1][neighbor_index[-1] % n_atoms < n_atoms_sys]
                elements_int_j = np.concatenate((
                    elements_int_sys[neighbor_index_sys % n_atoms], -np.ones(
                        len(neighbor_index[-1]) - len(neighbor_index_sys), dtype=int)))
                interaction_classes_j = atomic_classes[neighbor_index[-1] % n_atoms]
                atomic_charges_j = atomic_charges[neighbor_index[-1] % n_atoms]
            else:
                elements_int_j = elements_int_sys[neighbor_index[-1] % n_atoms]
                interaction_classes_j = np.empty(0, dtype=int)
                atomic_charges_j = np.empty(0, dtype=float)
            # append properties to ij lists
            ij_0.append(elements_int_j)
            ij_1.append(R_ij)
            ij_2.append(dR_ij__dalpha_i_)
            ij_3.append(interaction_classes_j)
            ij_4.append(atomic_charges_j)

            # triple properties
            if angular:
                ijk = get_triple_properties(
                    elements_int_j, R_ij, dR_ij__dalpha_i_, interaction_classes_j, atomic_charges_j,
                    self.settings.QMMM, calc_derivatives=calc_derivatives)
                # append properties to ijk lists
                ijk_0.append(ijk[0])
                ijk_1.append(ijk[1])
                ijk_2.append(ijk[2])
                ijk_3.append(ijk[3])
                ijk_4.append(ijk[4])
                ijk_5.append(ijk[5])
                ijk_6.append(ijk[6])
                ijk_7.append(ijk[7])
                ijk_8.append(ijk[8])
                ijk_9.append(ijk[9])
                ijk_10.append(ijk[10])
                ijk_11.append(ijk[11])
                ijk_12.append(ijk[12])

        # determine active atoms and the system neighbor indices lists of active environment atoms
        neighbor_index_env = typed.List()
        if self.settings.QMMM:
            # determine active atoms
            active_atom_env = np.unique(np.array([i for index in neighbor_index for i in index],
                                                 dtype=int) % n_atoms)
            if len(active_atom_env) > 0:
                active_atom_env = active_atom_env[atomic_classes[active_atom_env] == 2]
            active_atom = np.concatenate((np.arange(n_atoms_sys), active_atom_env))

            # handle periodic systems
            if len(lattice) > 0:
                # get adjacent periodic images of system atoms
                positions_sys_all = get_periodic_images(positions[:n_atoms_sys], lattice, n_atoms_sys)
                indices_sys = np.arange(27 * n_atoms_sys)
            # handle non-periodic systems
            else:
                positions_sys_all = positions[:n_atoms_sys]
                indices_sys = np.arange(n_atoms_sys)

            # determine system neighbor indices lists of active environment atoms
            if len(active_atom_env) > 0:
                for i in active_atom_env:
                    # calculate distances to system atoms
                    R_ij_env = np.sqrt(((positions_sys_all - positions[i])**2).sum(axis=1))
                    # determine neighbor atoms inside cutoff sphere
                    neighbors_env = np.less(R_ij_env, self.R_c)
                    # append neighbor indices lists of active environment atoms
                    neighbor_index_env.append(indices_sys[neighbors_env])
                    order_env = np.argsort(neighbor_index_env[-1] % n_atoms_sys)
                    neighbor_index_env[-1] = neighbor_index_env[-1][order_env]
            else:
                neighbor_index_env.append(np.arange(0))

        # set all atoms to be active if QM/MM is false
        else:
            active_atom = np.arange(n_atoms_sys)
            neighbor_index_env.append(np.arange(0))

        return neighbor_index, ij_0, ij_1, ij_2, ij_3, ij_4, ijk_0, ijk_1, ijk_2, ijk_3, ijk_4, \
            ijk_5, ijk_6, ijk_7, ijk_8, ijk_9, ijk_10, ijk_11, ijk_12, active_atom, \
            neighbor_index_env

####################################################################################################

    def get_H_parameters(self, H_type_j, H_type_jk):
        '''
        Implementation: Elements: H to Xe
                        Element parameters: 1, n, sp, d, 6-n, 9-sp, 11-d (all parameters need to be
                                            specified for all elements)
                        Exceptions: He: sp == 8 and 9-sp == 1, main group: d == 0 and 11-d == 0,
                                    d-block: sp == 0 and 9-sp == 0

        Return: H_parameters_rad, H_parameters_ang, n_H_parameters
        '''
        # implemented H parameters
        H_parameters = {'H':  [1, 1, 1,  0, 5, 8,  0],
                        'He': [1, 1, 8,  0, 5, 1,  0],
                        'Li': [1, 2, 1,  0, 4, 8,  0],
                        'Be': [1, 2, 2,  0, 4, 7,  0],
                        'B':  [1, 2, 3,  0, 4, 6,  0],
                        'C':  [1, 2, 4,  0, 4, 5,  0],
                        'N':  [1, 2, 5,  0, 4, 4,  0],
                        'O':  [1, 2, 6,  0, 4, 3,  0],
                        'F':  [1, 2, 7,  0, 4, 2,  0],
                        'Ne': [1, 2, 8,  0, 4, 1,  0],
                        'Na': [1, 3, 1,  0, 3, 8,  0],
                        'Mg': [1, 3, 2,  0, 3, 7,  0],
                        'Al': [1, 3, 3,  0, 3, 6,  0],
                        'Si': [1, 3, 4,  0, 3, 5,  0],
                        'P':  [1, 3, 5,  0, 3, 4,  0],
                        'S':  [1, 3, 6,  0, 3, 3,  0],
                        'Cl': [1, 3, 7,  0, 3, 2,  0],
                        'Ar': [1, 3, 8,  0, 3, 1,  0],
                        'K':  [1, 4, 1,  0, 2, 8,  0],
                        'Ca': [1, 4, 2,  0, 2, 7,  0],
                        'Sc': [1, 4, 2,  1, 2, 7, 10],
                        'Ti': [1, 4, 2,  2, 2, 7,  9],
                        'V':  [1, 4, 2,  3, 2, 7,  8],
                        'Cr': [1, 4, 2,  4, 2, 7,  7],
                        'Mn': [1, 4, 2,  5, 2, 7,  6],
                        'Fe': [1, 4, 2,  6, 2, 7,  5],
                        'Co': [1, 4, 2,  7, 2, 7,  4],
                        'Ni': [1, 4, 2,  8, 2, 7,  3],
                        'Cu': [1, 4, 2,  9, 2, 7,  2],
                        'Zn': [1, 4, 2, 10, 2, 7,  1],
                        'Ga': [1, 4, 3,  0, 2, 6,  0],
                        'Ge': [1, 4, 4,  0, 2, 5,  0],
                        'As': [1, 4, 5,  0, 2, 4,  0],
                        'Se': [1, 4, 6,  0, 2, 3,  0],
                        'Br': [1, 4, 7,  0, 2, 2,  0],
                        'Kr': [1, 4, 8,  0, 2, 1,  0],
                        'Rb': [1, 5, 1,  0, 1, 8,  0],
                        'Sr': [1, 5, 2,  0, 1, 7,  0],
                        'Y':  [1, 5, 2,  1, 1, 7, 10],
                        'Zr': [1, 5, 2,  2, 1, 7,  9],
                        'Nb': [1, 5, 2,  3, 1, 7,  8],
                        'Mo': [1, 5, 2,  4, 1, 7,  7],
                        'Tc': [1, 5, 2,  5, 1, 7,  6],
                        'Ru': [1, 5, 2,  6, 1, 7,  5],
                        'Rh': [1, 5, 2,  7, 1, 7,  4],
                        'Pd': [1, 5, 2,  8, 1, 7,  3],
                        'Ag': [1, 5, 2,  9, 1, 7,  2],
                        'Cd': [1, 5, 2, 10, 1, 7,  1],
                        'In': [1, 5, 3,  0, 1, 6,  0],
                        'Sn': [1, 5, 4,  0, 1, 5,  0],
                        'Sb': [1, 5, 5,  0, 1, 4,  0],
                        'Te': [1, 5, 6,  0, 1, 3,  0],
                        'I':  [1, 5, 7,  0, 1, 2,  0],
                        'Xe': [1, 5, 8,  0, 1, 1,  0]}
        H_parameters_max = [1, 5, 8, 10, 5, 8, 10]

        # determine H parameters
        n_H_parameters = len(H_parameters['H']) - 1
        H_parameters_rad = np.array([[H_parameters[ele][H_t_j] for H_t_j in H_type_j]
                                    for ele in self.element_types])
        H_parameters_rad_scale = np.array([1.0 / H_parameters_max[H_t_j] for H_t_j in H_type_j])
        H_parameters_ang = np.array([[H_parameters[ele][H_t_jk - n_H_parameters]
                                    if H_t_jk > n_H_parameters else H_parameters[ele][H_t_jk]
                                    for H_t_jk in H_type_jk] for ele in self.element_types])
        H_parameters_ang_scale = np.array([1.0 / H_parameters_max[H_t_jk - n_H_parameters]
                                          if H_t_jk > n_H_parameters else 0.5 / H_parameters_max[H_t_jk]
                                          for H_t_jk in H_type_jk])

        return H_parameters_rad, H_parameters_ang, H_parameters_rad_scale, H_parameters_ang_scale, \
            n_H_parameters

####################################################################################################

    def define_activation_function(self):
        '''
        Implementation: Activation function: sTanh, Tanh, Tanhshrink

        Return: activation_function
        '''
        # implemented activation function types
        activation_function_type_list = ['sTanh', 'Tanh', 'Tanhshrink']

        # activation function type sTanh
        if self.settings.activation_function_type == 'sTanh':
            activation_function = sTanh

        # activation function type Tanh
        elif self.settings.activation_function_type == 'Tanh':
            activation_function = torch.nn.Tanh

        # activation function type Tanhshrink
        elif self.settings.activation_function_type == 'Tanhshrink':
            activation_function = torch.nn.Tanhshrink

        # not implemented activation function type
        else:
            print('ERROR: Activation function type {0} is not yet implemented.'
                  .format(self.settings.activation_function_type),
                  '\nPlease use one of the following activation function types:')
            for act_fct_typ in activation_function_type_list:
                print('{0}'.format(act_fct_typ))
            sys.exit()

        return activation_function

####################################################################################################

    def define_model(self, model_index=0):
        '''
        Implementation: Model: HDNNP (with/without scale and shift layer)

        Modify: model
        '''
        # implemented model types
        model_type_list = ['HDNNP']

        # HDNNP model
        if self.settings.model_type == 'HDNNP':
            self.model[model_index] = torch.jit.script(HDNNP(
                self.n_element_types, self.n_descriptors, self.settings.n_neurons_hidden_layers,
                self.activation_function, self.settings.scale_shift_layer).to(self.device))

        # not implemented model type
        else:
            print('ERROR: Model type {0} is not yet implemented.'
                  .format(self.settings.model_type),
                  '\nPlease use one of the following model types:')
            for mod_typ in model_type_list:
                print('{0}'.format(mod_typ))
            sys.exit()

####################################################################################################

    def read_generalization(self, model_index=0):
        '''
        Implementation: lMLP, lMLP-only_prediction

        Modify: model, descriptor_parameters, R_c, element_energy
        '''
        # implemented generalization formats
        generalization_format_list = ['lMLP', 'lMLP-only_prediction']

        # read lMLP model
        if self.settings.generalization_format in ('lMLP', 'lMLP-only_prediction'):
            # check if generalization file exists
            if not path.isfile(self.settings.generalization_file):
                sys.exit('ERROR: Generalization file {0} does not exist.'.format(
                    self.settings.generalization_file))
            self.read_lMLP_model(model_index)

        # not implemented generalization format
        else:
            print('ERROR: Generalization format {0} is not yet implemented.'
                  .format(self.settings.generalization_format),
                  '\nPlease use one of the following formats:')
            for gen_format in generalization_format_list:
                print('{0}'.format(gen_format))
            sys.exit()

####################################################################################################

    def read_lMLP_model(self, model_index):
        '''
        Modify: model, descriptor_parameters, R_c, element_energy
        '''
        # read lMLP model
        checkpoint = torch.load(self.settings.generalization_file, weights_only=False)
        try:
            self.model[model_index].load_state_dict(checkpoint['model_state_dict'])
            self.descriptor_parameters = checkpoint['descriptor_parameters']
            self.R_c = checkpoint['R_c']
            self.element_energy = checkpoint['element_energy']
        except KeyError:
            sys.exit('ERROR: lMLP model file {0} is broken.'.format(
                self.settings.generalization_file))

####################################################################################################

    def calculate_energy_forces(self, model_index, n, elements_int_sys, descriptors_torch,
                                descriptor_derivatives_torch, neighbor_indices, n_atoms_sys,
                                descriptor_neighbor_derivatives_torch_env, neighbor_indices_env,
                                n_atoms_active, MM_gradients, create_graph=False):
        '''
        Reutrn: energy_prediction_torch, forces_prediction_torch
        '''
        # predict energy of fit structures
        energy_prediction_torch = self.model[model_index](elements_int_sys[n], descriptors_torch[n], n_atoms_sys[n])
        # predict forces of fit structures
        if self.settings.calc_forces:
            if self.settings.QMMM:
                forces_prediction_torch = calculate_forces_QMMM(
                    energy_prediction_torch, descriptors_torch[n], descriptor_derivatives_torch[0][n],
                    descriptor_derivatives_torch[1][n], neighbor_indices[n], n_atoms_sys[n],
                    descriptor_neighbor_derivatives_torch_env[n], neighbor_indices_env[n],
                    n_atoms_active[n], MM_gradients, create_graph=create_graph)
            else:
                forces_prediction_torch = calculate_forces(
                    energy_prediction_torch, descriptors_torch[n], descriptor_derivatives_torch[0][n],
                    descriptor_derivatives_torch[1][n], neighbor_indices[n], n_atoms_sys[n],
                    create_graph=create_graph)
        else:
            return energy_prediction_torch, torch.zeros((0, 3))

        return energy_prediction_torch, forces_prediction_torch

####################################################################################################

    def write_inputdata(self, inputdata_file, elements, positions, lattices, atomic_classes,
                        atomic_charges, energy, forces, n_structures, n_atoms, reorder, name=None,
                        assignment=None, uncertainty=None, counter=1, mode='w'):
        '''
        Output: inputdata file
        '''
        # write inputdata file
        with open(inputdata_file, mode, encoding='utf-8') as f:
            for n in range(n_structures):
                f.write('begin\n')
                f.write('comment number {0}\n'.format(counter))
                if name:
                    f.write('comment name {0}\n'.format(name[n]))
                if assignment:
                    f.write('comment data {0}\n'.format(assignment[n]))
                if uncertainty:
                    n_uncertainty = len(uncertainty[n])
                    f.write('comment uncertainty energy_per_atom {0:.8f}'.format(
                        round(uncertainty[n][0] / self.Hartree2eV, 8)))
                    if n_uncertainty > 1:
                        f.write(' forces_max {0:.6f}'.format(
                            round(uncertainty[n][1] / self.Hartree2eV * self.Bohr2Angstrom, 6)))
                    if n_uncertainty > 2:
                        f.write(' forces_max_env {0:.6f}\n'.format(
                            round(uncertainty[n][2] / self.Hartree2eV * self.Bohr2Angstrom, 6)))
                    else:
                        f.write('\n')
                if len(lattices[n]) > 0:
                    for i in range(3):
                        f.write('lattice {0:>10.6f} {1:>10.6f} {2:>10.6f}\n'
                                .format(round(lattices[n][i][0] / self.Bohr2Angstrom, 6),
                                        round(lattices[n][i][1] / self.Bohr2Angstrom, 6),
                                        round(lattices[n][i][2] / self.Bohr2Angstrom, 6)))
                element = elements[n]
                position = positions[n] / self.Bohr2Angstrom
                atomic_class = atomic_classes[n].astype(float)
                atomic_charge = atomic_charges[n]
                force = forces[n] / self.Hartree2eV * self.Bohr2Angstrom
                if self.settings.QMMM:
                    element = element[reorder[n]]
                    position = position[reorder[n]]
                    atomic_class = atomic_class[reorder[n]]
                    atomic_charge = atomic_charge[reorder[n]]
                    force = force[reorder[n]]
                for i in range(n_atoms[n]):
                    f.write('atom {0:>10.6f} {1:>10.6f} {2:>10.6f} {3:2} {4:3.1f} {5:>6.3f} '
                            .format(round(position[i][0], 6), round(position[i][1], 6),
                                    round(position[i][2], 6), element[i], atomic_class[i],
                                    round(atomic_charge[i], 3)))
                    f.write('{0:>10.6f} {1:>10.6f} {2:>10.6f}\n'.format(
                        round(force[i][0], 6), round(force[i][1], 6), round(force[i][2], 6)))
                f.write('energy {0:.8f}\ncharge 0.0\nend\n'.format(
                    round(energy[n] / self.Hartree2eV, 8)))
                counter += 1


####################################################################################################

####################################################################################################

@torch.jit.interface
class ModuleInterface(torch.nn.Module):
    '''
    Interface for just-in-time compilation of HDNNP model with TorchScript, while the atomic neural
    networks can be accessed by integer literals
    '''

####################################################################################################

    def forward(self, input: torch.Tensor) -> torch.Tensor:   # type: ignore[empty-body]
        '''
        Return: energy_prediction_torch
        '''
        pass   # pylint: disable=unnecessary-pass


####################################################################################################

####################################################################################################

class HDNNP(torch.nn.Module):
    '''
    HDNNP model
    '''

####################################################################################################

    def __init__(self, n_element_types: int, n_descriptors: int, n_neurons_hidden_layers: List[int],
                 activation_function: Any, scale_shift_layer: bool) -> None:
        '''
        Initialization
        '''
        # initialize HDNNP parameters
        super().__init__()
        self.n_element_types = n_element_types
        self.n_descriptors = n_descriptors
        self.n_neurons_hidden_layers = n_neurons_hidden_layers
        self.N_hidden_layers = len(n_neurons_hidden_layers)
        self.activation_function = activation_function
        self.scale_shift_layer = scale_shift_layer

        # initialize HDNNP architecture
        self.atomic_neural_networks = torch.nn.ModuleList()
        for i_element in range(self.n_element_types):
            self.atomic_neural_networks.append(torch.nn.Sequential())
            if self.scale_shift_layer:
                self.atomic_neural_networks[i_element].append(Standardization(self.n_descriptors))
            self.atomic_neural_networks[i_element].append(
                torch.nn.Linear(self.n_descriptors, self.n_neurons_hidden_layers[0]))
            self.atomic_neural_networks[i_element].append(self.activation_function())
            for i_layer in range(self.N_hidden_layers - 1):
                self.atomic_neural_networks[i_element].append(
                    torch.nn.Linear(self.n_neurons_hidden_layers[i_layer],
                                    self.n_neurons_hidden_layers[i_layer + 1]))
                self.atomic_neural_networks[i_element].append(self.activation_function())
            self.atomic_neural_networks[i_element].append(
                torch.nn.Linear(self.n_neurons_hidden_layers[-1], 1))

####################################################################################################

    def forward(self, elements_int_sys: List[int], descriptors_torch: Tensor,
                n_atoms_sys: int) -> Tensor:
        '''
        Return: energy_prediction_torch
        '''
        # calculate energy prediction
        E = torch.empty(n_atoms_sys)
        for i in range(n_atoms_sys):
            ann: ModuleInterface = self.atomic_neural_networks[elements_int_sys[i]]
            E[i] = ann.forward(descriptors_torch[i])[0]
        energy_prediction_torch = torch.sum(E, 0, keepdim=True)

        return energy_prediction_torch


####################################################################################################

####################################################################################################

@torch.jit.script
def calculate_forces(energy_prediction_torch: Tensor, descriptors_torch: Tensor,
                     descriptor_i_derivatives_torch: List[Tensor],
                     descriptor_neighbor_derivatives_torch: List[Tensor],
                     neighbor_indices: List[List[int]], n_atoms_active: int,
                     create_graph: bool = True) -> Tensor:
    '''
    Return: forces_prediction_torch
    '''
    # initialize forces prediction
    forces_prediction_torch = torch.zeros((n_atoms_active, 3))
    # calculate model gradient
    model_gradient = torch.autograd.grad(
        [energy_prediction_torch], [descriptors_torch], create_graph=create_graph)[0]
    assert isinstance(model_gradient, Tensor)
    # combine model gradient and descriptor gradient
    for i in range(n_atoms_active):
        forces_prediction_torch[i] -= torch.sum(
            torch.t(model_gradient[i] * torch.t(descriptor_i_derivatives_torch[i])), 0)
        forces_prediction_torch[i] -= torch.sum(
            torch.t(torch.flatten(model_gradient[neighbor_indices[i]], -2, -1) * torch.t(
                torch.flatten(descriptor_neighbor_derivatives_torch[i], -3, -2))), 0)

    return forces_prediction_torch


####################################################################################################

@torch.jit.script
def calculate_forces_QMMM(energy_prediction_torch: Tensor, descriptors_torch: Tensor,
                          descriptor_i_derivatives_torch: List[Tensor],
                          descriptor_neighbor_derivatives_torch: List[Tensor],
                          neighbor_indices: List[List[int]], n_atoms_sys: int,
                          descriptor_neighbor_derivatives_torch_env: List[Tensor],
                          neighbor_indices_env: List[List[int]], n_atoms_active: int,
                          MM_gradients: List[int], create_graph: bool = True) -> Tensor:
    '''
    Return: forces_prediction_torch
    '''
    # initialize forces prediction
    forces_prediction_torch = torch.zeros((n_atoms_active, 3))
    # calculate model gradient
    model_gradient = torch.autograd.grad(
        [energy_prediction_torch], [descriptors_torch], create_graph=create_graph)[0]
    assert isinstance(model_gradient, Tensor)
    # combine model gradient and descriptor gradient
    for i in range(n_atoms_sys):
        forces_prediction_torch[i] -= torch.sum(
            torch.t(model_gradient[i] * torch.t(descriptor_i_derivatives_torch[i])), 0)
        forces_prediction_torch[i] -= torch.sum(
            torch.t(torch.flatten(model_gradient[neighbor_indices[i]], -2, -1) * torch.t(
                torch.flatten(descriptor_neighbor_derivatives_torch[i], -3, -2))), 0)
    for i in range(n_atoms_active - n_atoms_sys):
        forces_prediction_torch[i + n_atoms_sys] -= torch.sum(
            torch.t(torch.flatten(model_gradient[neighbor_indices_env[i]][:, MM_gradients], -2, -1) * torch.t(
                torch.flatten(descriptor_neighbor_derivatives_torch_env[i], -3, -2))), 0)

    return forces_prediction_torch


####################################################################################################

####################################################################################################

@ncfjit
def prepare_periodic_cell(positions, lattice, n_atoms, n_atoms_sys, R_c) -> Tuple[
        NDArray, NDArray, bool, int]:
    '''
    Return: positions, lattice, pbc_required, n_images_tot
    '''
    # get fractional coordinates
    positions = np.linalg.solve(lattice.T, positions.T).T

    # for QM/MM align center of system atoms and center of cell
    if n_atoms_sys < n_atoms:
        positions -= (np.sum(positions[:n_atoms_sys], axis=0) / n_atoms_sys - 0.5)

    # wrap atoms into original cell
    positions %= 1.0

    # determine if periodic boundary conditions are required according to the space between atoms in
    # the original cell and those in neighboring cells employing the minimal and maximal fractional
    # coordinates in each direction and the respective height of the cell
    normal = [np.cross(lattice[1], lattice[2]),
              np.cross(lattice[2], lattice[0]),
              np.cross(lattice[0], lattice[1])]
    normal = [normal[0] / np.sqrt(np.dot(normal[0], normal[0])),
              normal[1] / np.sqrt(np.dot(normal[1], normal[1])),
              normal[2] / np.sqrt(np.dot(normal[2], normal[2]))]
    height = [abs(np.dot(normal[0], lattice[0])),
              abs(np.dot(normal[1], lattice[1])),
              abs(np.dot(normal[2], lattice[2]))]
    if n_atoms_sys < n_atoms:
        pbc = np.array([(np.min(positions[:n_atoms_sys, 0]) + 1.0 - np.max(positions[:, 0]))
                        * height[0] < R_c,
                        (np.min(positions[:n_atoms_sys, 1]) + 1.0 - np.max(positions[:, 1]))
                        * height[1] < R_c,
                        (np.min(positions[:n_atoms_sys, 2]) + 1.0 - np.max(positions[:, 2]))
                        * height[2] < R_c,
                        (np.min(positions[:, 0]) + 1.0 - np.max(positions[:n_atoms_sys, 0]))
                        * height[0] < R_c,
                        (np.min(positions[:, 1]) + 1.0 - np.max(positions[:n_atoms_sys, 1]))
                        * height[1] < R_c,
                        (np.min(positions[:, 2]) + 1.0 - np.max(positions[:n_atoms_sys, 2]))
                        * height[2] < R_c])
    else:
        pbc = np.array([(np.min(positions[:, 0]) + 1.0 - np.max(positions[:, 0]))
                        * height[0] < R_c,
                        (np.min(positions[:, 1]) + 1.0 - np.max(positions[:, 1]))
                        * height[1] < R_c,
                        (np.min(positions[:, 2]) + 1.0 - np.max(positions[:, 2]))
                        * height[2] < R_c])
    pbc_required = bool(np.any(pbc))

    # reconvert fractional coordinates
    positions = np.dot(positions, lattice)

    # expand cell if its heights are smaller than the cutoff radius
    n_images_tot = 1
    if pbc_required:
        for i in range(3):
            if height[i] < R_c:
                n_images = int(R_c / height[i]) + 1
                positions = (np.ones((n_images, n_atoms, 3)) * positions).reshape((
                    n_images * n_atoms, 3))
                for j in range(1, n_images):
                    positions[j * n_atoms:(j + 1) * n_atoms] += j * lattice[i]
                lattice[i] *= n_images
                n_atoms *= n_images
                n_images_tot *= n_images

    return positions, lattice, pbc_required, n_images_tot


####################################################################################################

@ncfjit
def get_periodic_images(positions, lattice, n_atoms) -> NDArray:
    '''
    Return: positions_all
    '''
    # get adjacent periodic images (3x3x3 supercell)
    positions_all = (np.ones((27, n_atoms, 3)) * positions).reshape((27 * n_atoms, 3))
    positions_all[1 * n_atoms:10 * n_atoms] -= lattice[0]
    positions_all[18 * n_atoms:27 * n_atoms] += lattice[0]
    positions_all[1 * n_atoms:4 * n_atoms] -= lattice[1]
    positions_all[7 * n_atoms:10 * n_atoms] += lattice[1]
    positions_all[10 * n_atoms:13 * n_atoms] -= lattice[1]
    positions_all[15 * n_atoms:18 * n_atoms] += lattice[1]
    positions_all[18 * n_atoms:21 * n_atoms] -= lattice[1]
    positions_all[24 * n_atoms:27 * n_atoms] += lattice[1]
    for i in range(1, 13, 3):
        positions_all[i * n_atoms:(i + 1) * n_atoms] -= lattice[2]
        positions_all[(i + 2) * n_atoms:(i + 3) * n_atoms] += lattice[2]
    positions_all[13 * n_atoms:14 * n_atoms] -= lattice[2]
    positions_all[14 * n_atoms:15 * n_atoms] += lattice[2]
    for i in range(15, 27, 3):
        positions_all[i * n_atoms:(i + 1) * n_atoms] -= lattice[2]
        positions_all[(i + 2) * n_atoms:(i + 3) * n_atoms] += lattice[2]

    return positions_all


####################################################################################################

@ncfjit
def get_triple_properties(elements_int_j, R_ij, dR_ij__dalpha_i_, interaction_classes_j,
                          atomic_charges_j, QMMM, calc_derivatives=True):
    '''
    Return: ijk
    '''
    # initialize arrays
    n_neighbors = len(R_ij)
    M = (n_neighbors - 1) * n_neighbors // 2
    ijk_0, ijk_1 = np.empty(M, dtype=np.int64), np.empty(M, dtype=np.int64)
    ijk_2, ijk_3, ijk_6 = np.empty(M, dtype=float), np.empty(M, dtype=float), \
        np.empty(M, dtype=float)

    # initialize arrays for derivative properties
    if calc_derivatives:
        M_prime = M
    else:
        M_prime = 0
    ijk_4, ijk_5, ijk_7, ijk_8, ijk_9 = np.empty((M_prime, 3), dtype=float), \
        np.empty((M_prime, 3), dtype=float), np.empty((M_prime, 3), dtype=float), \
        np.empty((M_prime, 3), dtype=float), np.empty((M_prime, 3), dtype=float)

    # initialize arrays for QM/MM properties
    if QMMM:
        M_QMMM = M
    else:
        M_QMMM = 0
    ijk_10 = np.empty(M_QMMM, dtype=np.int64)
    ijk_11, ijk_12 = np.empty(M_QMMM, dtype=float), np.empty(M_QMMM, dtype=float)

    # get all unique neighbor combinations (no double counting)
    j, k = np.triu_indices(n_neighbors, k=1)
    m = j * (2 * n_neighbors - j - 3) // 2 + k - 1

    # insert properties into arrays
    ijk_0[m] = elements_int_j[j]
    ijk_1[m] = elements_int_j[k]
    ijk_2[m] = R_ij[j]
    ijk_3[m] = R_ij[k]
    # calculate cos(theta)
    cos_theta = np.minimum(np.maximum(np.dot(dR_ij__dalpha_i_, dR_ij__dalpha_i_.T),
                           -0.999999999999), 0.999999999999)
    cos_theta_ijk = np.empty(M, dtype=float)
    for i in range(M):
        cos_theta_ijk[i] = cos_theta[j[i], k[i]]
    ijk_6[m] = cos_theta_ijk

    # insert derivative properties into arrays
    if calc_derivatives:
        ijk_4[m] = dR_ij__dalpha_i_[j]
        ijk_5[m] = dR_ij__dalpha_i_[k]
        # calculate the derivative of cos(theta)
        j1 = (dR_ij__dalpha_i_[j].T / R_ij[k]).T
        j2 = (dR_ij__dalpha_i_[j].T / R_ij[j]).T
        k1 = (dR_ij__dalpha_i_[k].T / R_ij[j]).T
        k2 = (dR_ij__dalpha_i_[k].T / R_ij[k]).T
        ijk_7[m] = j1 + k1 - (cos_theta_ijk * (j2 + k2).T).T
        ijk_8[m] = -k1 + (cos_theta_ijk * j2.T).T
        ijk_9[m] = -j1 + (cos_theta_ijk * k2.T).T

    # insert QM/MM properties into arrays
    if QMMM:
        ijk_10[m] = interaction_classes_j[j] + interaction_classes_j[k]
        ijk_11[m] = atomic_charges_j[j]
        ijk_12[m] = atomic_charges_j[k]

    return (ijk_0, ijk_1, ijk_2, ijk_3, ijk_4, ijk_5, ijk_6, ijk_7, ijk_8, ijk_9, ijk_10, ijk_11,
            ijk_12)


####################################################################################################

@ncfjit
def calc_descriptor_derivative(
        ij_0, ij_1, ij_2, ij_3, ij_4, ijk_0, ijk_1, ijk_2, ijk_3, ijk_4, ijk_5, ijk_6, ijk_7, ijk_8,
        ijk_9, ijk_10, ijk_11, ijk_12, neighbor_index, n_atoms, n_atoms_sys, n_descriptors,
        elem_func_index, rad_func_index, ang_func_index, scale_func_index, R_c, eta_ij,
        H_parameters_rad, H_parameters_rad_scale, n_parameters_rad, element_types_rad, eta_ijk,
        lambda_ijk, zeta_ijk, xi_ijk, H_parameters_ang, H_parameters_ang_scale,
        n_parameters_ang, H_type_jk, n_H_parameters, element_types_ang, calc_derivatives, QMMM,
        active_atom, n_atoms_active, neighbor_index_env, I_type_j, n_parameters_rad_env,
        I_type_jk, n_parameters_ang_env, MM_atomic_charge_max) -> Tuple[
            List[NDArray], List[NDArray], List[NDArray], List[NDArray]]:
    '''
    Return: descriptor, descriptor_i_derivative, descriptor_neighbor_derivative,
            descriptor_neighbor_derivative_env
    '''
    # calculate symmetry function values and derivatives
    descriptor = [np.zeros(0)] * n_atoms_sys
    descriptor_i_derivative = [np.zeros((0, 3))] * n_atoms_sys
    descriptor_neighbor_derivative = [np.zeros((0, 0, 3))] * n_atoms_sys
    descriptor_j_derivatives_rad = [np.zeros((0, 0, 3))] * n_atoms_sys
    descriptor_j_derivatives_ang = [np.zeros((0, 0, 3))] * n_atoms_sys
    descriptor_k_derivatives_ang = [np.zeros((0, 0, 3))] * n_atoms_sys
    # radial and angular symmetry functions
    for i in range(n_atoms_sys):
        G_rad, dG_rad__dalpha_i_, dG_rad__dalpha_j_ = calc_rad_sym_func(
            ij_0[i], ij_1[i], ij_2[i], ij_3[i], ij_4[i], elem_func_index, rad_func_index,
            scale_func_index, R_c, eta_ij, H_parameters_rad, H_parameters_rad_scale,
            n_parameters_rad, element_types_rad, calc_derivatives, QMMM, I_type_j,
            MM_atomic_charge_max)
        G_ang, dG_ang__dalpha_i_, dG_ang__dalpha_j_, dG_ang__dalpha_k_ = calc_ang_sym_func(
            ijk_0[i], ijk_1[i], ijk_2[i], ijk_3[i], ijk_4[i], ijk_5[i], ijk_6[i], ijk_7[i],
            ijk_8[i], ijk_9[i], ijk_10[i], ijk_11[i], ijk_12[i], elem_func_index, rad_func_index,
            ang_func_index, scale_func_index, R_c, eta_ijk, lambda_ijk, zeta_ijk, xi_ijk,
            H_parameters_ang, H_parameters_ang_scale, n_parameters_ang, H_type_jk, n_H_parameters,
            element_types_ang, calc_derivatives, QMMM, I_type_jk, MM_atomic_charge_max)
        # compile symmetry function values
        descriptor[i] = np.concatenate((G_rad, G_ang))
        # compile symmetry function derivatives with respect to central atom i
        if calc_derivatives:
            descriptor_i_derivative[i] = np.concatenate((dG_rad__dalpha_i_, dG_ang__dalpha_i_))
            # compile symmetry function derivatives with respect to neighbor atoms j and k
            descriptor_j_derivatives_rad[i] = dG_rad__dalpha_j_
            descriptor_j_derivatives_ang[i] = dG_ang__dalpha_j_
            descriptor_k_derivatives_ang[i] = dG_ang__dalpha_k_
    # calculate symmetry function derivatives with respect to neighbor atoms of atom i
    if calc_derivatives:
        for i in range(n_atoms_sys):
            n_neighbors = len(neighbor_index[i][neighbor_index[i] % n_atoms < n_atoms_sys])
            if n_neighbors > 0:
                descriptor_neighbor_derivative[i] = np.zeros((n_neighbors, n_descriptors, 3))
                for j in range(n_neighbors):
                    if neighbor_index[i][j] >= n_atoms:
                        index = (27 - neighbor_index[i][j] // n_atoms) * n_atoms + i
                    else:
                        index = i
                    descriptor_neighbor_derivative[i][j] = calc_descriptor_neighbor_derivative(
                        descriptor_j_derivatives_rad[neighbor_index[i][j] % n_atoms],
                        descriptor_j_derivatives_ang[neighbor_index[i][j] % n_atoms],
                        descriptor_k_derivatives_ang[neighbor_index[i][j] % n_atoms], index,
                        neighbor_index[neighbor_index[i][j] % n_atoms], n_descriptors,
                        n_parameters_rad, n_parameters_ang, 0, 0)

    # calculate symmetry function derivatives with respect to neighbor active environment atoms of
    # atom i
    if QMMM and calc_derivatives:
        n_descriptors_env = n_parameters_rad_env + n_parameters_ang_env
        n_parameters_rad_env_start = n_parameters_rad - n_parameters_rad_env
        n_parameters_ang_env_start = n_parameters_ang - n_parameters_ang_env
        n_atoms_env = n_atoms_active - n_atoms_sys
        descriptor_neighbor_derivative_env = [np.zeros((0, 0, 3))] * n_atoms_env
        for i in range(n_atoms_env):
            n_neighbors_env = len(neighbor_index_env[i])
            if n_neighbors_env > 0:
                descriptor_neighbor_derivative_env[i] = np.zeros((
                    n_neighbors_env, n_descriptors_env, 3))
                for j in range(n_neighbors_env):
                    if neighbor_index_env[i][j] >= n_atoms_sys:
                        index = ((27 - neighbor_index_env[i][j] // n_atoms_sys) * n_atoms
                                 + active_atom[i + n_atoms_sys])
                    else:
                        index = active_atom[i + n_atoms_sys]
                    descriptor_neighbor_derivative_env[i][j] = calc_descriptor_neighbor_derivative(
                        descriptor_j_derivatives_rad[neighbor_index_env[i][j] % n_atoms_sys],
                        descriptor_j_derivatives_ang[neighbor_index_env[i][j] % n_atoms_sys],
                        descriptor_k_derivatives_ang[neighbor_index_env[i][j] % n_atoms_sys],
                        index, neighbor_index[neighbor_index_env[i][j] % n_atoms_sys],
                        n_descriptors_env, n_parameters_rad_env, n_parameters_ang_env,
                        n_parameters_rad_env_start, n_parameters_ang_env_start)
    else:
        descriptor_neighbor_derivative_env = [np.zeros((0, 0, 3))]

    return descriptor, descriptor_i_derivative, descriptor_neighbor_derivative, \
        descriptor_neighbor_derivative_env


####################################################################################################

@ncfjit
def calc_descriptor_derivative_radial(
        ij_0, ij_1, ij_2, ij_3, ij_4, neighbor_index, n_atoms, n_atoms_sys, n_descriptors,
        elem_func_index, rad_func_index, scale_func_index, R_c, eta_ij, H_parameters_rad,
        H_parameters_rad_scale, n_parameters_rad, element_types_rad, calc_derivatives, QMMM,
        active_atom, n_atoms_active, neighbor_index_env, I_type_j, n_parameters_rad_env,
        MM_atomic_charge_max) -> Tuple[List[NDArray], List[NDArray], List[NDArray], List[NDArray]]:
    '''
    Return: descriptor, descriptor_i_derivative, descriptor_neighbor_derivative,
            descriptor_neighbor_derivative_env
    '''
    # calculate symmetry function values and derivatives
    descriptor = [np.zeros(0)] * n_atoms_sys
    descriptor_i_derivative = [np.zeros((0, 3))] * n_atoms_sys
    descriptor_neighbor_derivative = [np.zeros((0, 0, 3))] * n_atoms_sys
    descriptor_j_derivatives_rad = [np.zeros((0, 0, 3))] * n_atoms_sys
    zeros = np.zeros((0, 0, 0))
    # only radial symmetry functions
    for i in range(n_atoms_sys):
        descriptor[i], dG_rad__dalpha_i_, dG_rad__dalpha_j_ = calc_rad_sym_func(
            ij_0[i], ij_1[i], ij_2[i], ij_3[i], ij_4[i], elem_func_index, rad_func_index,
            scale_func_index, R_c, eta_ij, H_parameters_rad, H_parameters_rad_scale,
            n_parameters_rad, element_types_rad, calc_derivatives, QMMM, I_type_j,
            MM_atomic_charge_max)
        # compile symmetry function values
        if calc_derivatives:
            # compile symmetry function derivatives with respect to central atom i
            descriptor_i_derivative[i] = np.concatenate((dG_rad__dalpha_i_, np.zeros((0, 3))))
            # compile symmetry function derivatives with respect to neighbor atoms j
            descriptor_j_derivatives_rad[i] = dG_rad__dalpha_j_
    # calculate symmetry function derivatives with respect to neighbor atoms of atom i
    if calc_derivatives:
        for i in range(n_atoms_sys):
            n_neighbors = len(neighbor_index[i][neighbor_index[i] % n_atoms < n_atoms_sys])
            if n_neighbors > 0:
                descriptor_neighbor_derivative[i] = np.zeros((n_neighbors, n_descriptors, 3))
                for j in range(n_neighbors):
                    if neighbor_index[i][j] >= n_atoms:
                        index = (27 - neighbor_index[i][j] // n_atoms) * n_atoms + i
                    else:
                        index = i
                    descriptor_neighbor_derivative[i][j] = calc_descriptor_neighbor_derivative(
                        descriptor_j_derivatives_rad[neighbor_index[i][j] % n_atoms], zeros, zeros,
                        index, neighbor_index[neighbor_index[i][j] % n_atoms], n_descriptors,
                        n_parameters_rad, 0, 0, 0)

    # calculate symmetry function derivatives with respect to neighbor active environment atoms of
    # atom i
    if QMMM and calc_derivatives:
        n_atoms_env = n_atoms_active - n_atoms_sys
        n_parameters_rad_env_start = n_parameters_rad - n_parameters_rad_env
        descriptor_neighbor_derivative_env = [np.zeros((0, 0, 3))] * n_atoms_env
        for i in range(n_atoms_env):
            n_neighbors_env = len(neighbor_index_env[i])
            if n_neighbors_env > 0:
                descriptor_neighbor_derivative_env[i] = np.zeros((
                    n_neighbors_env, n_parameters_rad_env, 3))
                for j in range(n_neighbors_env):
                    if neighbor_index_env[i][j] >= n_atoms_sys:
                        index = ((27 - neighbor_index_env[i][j] // n_atoms_sys) * n_atoms
                                 + active_atom[i + n_atoms_sys])
                    else:
                        index = active_atom[i + n_atoms_sys]
                    descriptor_neighbor_derivative_env[i][j] = calc_descriptor_neighbor_derivative(
                        descriptor_j_derivatives_rad[neighbor_index_env[i][j] % n_atoms_sys], zeros,
                        zeros, index, neighbor_index[neighbor_index_env[i][j] % n_atoms_sys],
                        n_parameters_rad_env, n_parameters_rad_env, 0, n_parameters_rad_env_start, 0)
    else:
        descriptor_neighbor_derivative_env = [np.zeros((0, 0, 3))]

    return descriptor, descriptor_i_derivative, descriptor_neighbor_derivative, \
        descriptor_neighbor_derivative_env


####################################################################################################

@ncfjit
def calc_descriptor_neighbor_derivative(descriptor_j_derivatives_rad_neighbor,
                                        descriptor_j_derivatives_ang_neighbor,
                                        descriptor_k_derivatives_ang_neighbor, index,
                                        neighbor_indices_neighbor, n_descriptors,
                                        n_parameters_rad, n_parameters_ang,
                                        n_parameters_rad_start, n_parameters_ang_start) -> NDArray:
    '''
    Return: descriptor_neighbor_derivative
    '''
    # calculate descriptor neighbor derivative
    descriptor_neighbor_derivative = np.zeros((n_descriptors, 3))
    n_neighbor_neighbors = len(neighbor_indices_neighbor)
    i_neighbor_index = np.argwhere(neighbor_indices_neighbor == index)[0][0]

    # radial symmetry functions
    descriptor_neighbor_derivative[:n_parameters_rad] = descriptor_j_derivatives_rad_neighbor[
        n_parameters_rad_start:n_parameters_rad_start + n_parameters_rad, i_neighbor_index]

    # angular symmetry functions
    if n_parameters_ang > 0:
        for k in range(i_neighbor_index + 1, n_neighbor_neighbors):
            m = i_neighbor_index * (2 * n_neighbor_neighbors - i_neighbor_index - 3) // 2 + k - 1
            descriptor_neighbor_derivative[n_parameters_rad:] += descriptor_j_derivatives_ang_neighbor[
                n_parameters_ang_start:n_parameters_ang_start + n_parameters_ang, m]
        for j in range(i_neighbor_index):
            m = j * (2 * n_neighbor_neighbors - j - 3) // 2 + i_neighbor_index - 1
            descriptor_neighbor_derivative[n_parameters_rad:] += descriptor_k_derivatives_ang_neighbor[
                n_parameters_ang_start:n_parameters_ang_start + n_parameters_ang, m]

    return descriptor_neighbor_derivative


####################################################################################################

@ncfjit
def calc_rad_sym_func(elements_int_j, ij_1, dR_ij__dalpha_i_, interaction_classes_j,
                      atomic_charges_j, elem_func_index, rad_func_index, scale_func_index, R_c,
                      eta_ij, H_parameters_rad, H_parameters_rad_scale, n_parameters_rad,
                      element_types_rad, calc_derivatives, QMMM, I_type_j,
                      MM_atomic_charge_max) -> Tuple[NDArray, NDArray, NDArray]:
    '''
    Requirement: 0 <= R_ij < R_c

    Return: G_rad, dG_rad__dalpha_i_, dG_rad__dalpha_j_
    '''
    # check if neighbors exist
    n_interactions = len(elements_int_j)
    if n_interactions == 0:
        return np.zeros(n_parameters_rad), np.zeros((n_parameters_rad, 3)), \
            np.zeros((n_parameters_rad, 0, 3))

    # determine element-dependent radial function
    if elem_func_index == 0:
        elem_j = elem_rad_eeACSF(
            elements_int_j, n_parameters_rad, H_parameters_rad, H_parameters_rad_scale,
            n_interactions)
    elif elem_func_index == 1:
        elem_j = elem_rad_ACSF(
            elements_int_j, n_parameters_rad, element_types_rad, n_interactions)
    elif elem_func_index == 2:
        elem_j = elem_rad_eeACSF_QMMM(
            elements_int_j, interaction_classes_j, atomic_charges_j, n_parameters_rad,
            H_parameters_rad, H_parameters_rad_scale, n_interactions, MM_atomic_charge_max)

    # determine interaction-dependent radial function
    if QMMM:
        int_j = int_rad_eeACSF_QMMM(interaction_classes_j, I_type_j, n_parameters_rad,
                                    n_interactions)
        elem_j = elem_j * int_j

    # calculate combined radial and cutoff function and its derivative
    R_ij = ij_1.repeat(n_parameters_rad).reshape((-1, n_parameters_rad))
    if rad_func_index == 0:
        rad_ij, drad_ij = rad_bump(R_ij, eta_ij, R_c)
    elif rad_func_index == 1:
        rad_ij, drad_ij = rad_gaussian_bump(R_ij, eta_ij, R_c)
    elif rad_func_index == 2:
        rad_ij, drad_ij = rad_gaussian_cos(R_ij, eta_ij, R_c)

    # calculate unscaled radial eeACSFs
    G_rad = np.sum(elem_j * rad_ij, axis=0)

    # calculate radial eeACSF derivatives
    if calc_derivatives:
        if scale_func_index == 0:
            dscale = dscale_crss(G_rad)
        elif scale_func_index == 1:
            dscale = dscale_linear(G_rad)
        elif scale_func_index == 2:
            dscale = dscale_sqrt(G_rad)
        dG_rad__dalpha_j_ = ((-dscale * elem_j * drad_ij) * np.ones((
            3, n_interactions, n_parameters_rad))).T * dR_ij__dalpha_i_
        dG_rad__dalpha_i_ = -np.sum(dG_rad__dalpha_j_, axis=1)

    # calculate radial eeACSFs
    if scale_func_index == 0:
        G_rad = scale_crss(G_rad)
    elif scale_func_index == 1:
        G_rad = scale_linear(G_rad)
    elif scale_func_index == 2:
        G_rad = scale_sqrt(G_rad)

    if not calc_derivatives:
        return G_rad, np.zeros((0, 3)), np.zeros((0, 0, 3))

    return G_rad, dG_rad__dalpha_i_, dG_rad__dalpha_j_


####################################################################################################

@ncfjit
def calc_ang_sym_func(elements_int_j, elements_int_k, ijk_2, ijk_3, dR_ij__dalpha_i_,
                      dR_ik__dalpha_i_, ijk_6, dcos_theta_ijk__dalpha_i_, dcos_theta_ijk__dalpha_j_,
                      dcos_theta_ijk__dalpha_k_, interaction_classes_jk, atomic_charges_j,
                      atomic_charges_k, elem_func_index, rad_func_index, ang_func_index,
                      scale_func_index, R_c, eta_ijk, lambda_ijk, zeta_ijk, xi_ijk, H_parameters_ang,
                      H_parameters_ang_scale, n_parameters_ang, H_type_jk, n_H_parameters,
                      element_types_ang, calc_derivatives, QMMM, I_type_jk,
                      MM_atomic_charge_max) -> Tuple[NDArray, NDArray, NDArray, NDArray]:
    '''
    Requirement: 0 <= R_ij < R_c, 0 <= R_ik < R_c

    Return: G_ang, dG_ang__dalpha_i_, dG_ang__dalpha_j_, dG_ang__dalpha_k_
    '''
    # check if neighbors exist
    n_interactions = len(elements_int_j)
    if n_interactions == 0:
        return np.zeros(n_parameters_ang), np.zeros((n_parameters_ang, 3)), \
            np.zeros((n_parameters_ang, 0, 3)), np.zeros((n_parameters_ang, 0, 3))

    # determine element-dependent angular function
    if elem_func_index == 0:
        elem_jk = elem_ang_eeACSF(
            elements_int_j, elements_int_k, n_parameters_ang, H_parameters_ang,
            H_parameters_ang_scale, H_type_jk, n_H_parameters, n_interactions)
    elif elem_func_index == 1:
        elem_jk = elem_ang_ACSF(
            elements_int_j, elements_int_k, n_parameters_ang, element_types_ang, n_interactions)
    elif elem_func_index == 2:
        elem_jk = elem_ang_eeACSF_QMMM(
            elements_int_j, elements_int_k, interaction_classes_jk, atomic_charges_j,
            atomic_charges_k, n_parameters_ang, H_parameters_ang, H_parameters_ang_scale, H_type_jk,
            n_H_parameters, I_type_jk, n_interactions, MM_atomic_charge_max)

    # determine interaction-dependent angular function
    if QMMM:
        int_jk = int_ang_eeACSF_QMMM(interaction_classes_jk, I_type_jk, n_parameters_ang,
                                     n_interactions)
        elem_jk = elem_jk * int_jk

    # calculate radial functions and their derivatives
    R_ij = ijk_2.repeat(n_parameters_ang).reshape((-1, n_parameters_ang))
    R_ik = ijk_3.repeat(n_parameters_ang).reshape((-1, n_parameters_ang))
    if rad_func_index == 0:
        rad_ij, drad_ij = rad_bump(R_ij, eta_ijk, R_c)
        rad_ik, drad_ik = rad_bump(R_ik, eta_ijk, R_c)
    elif rad_func_index == 1:
        rad_ij, drad_ij = rad_gaussian_bump(R_ij, eta_ijk, R_c)
        rad_ik, drad_ik = rad_gaussian_bump(R_ik, eta_ijk, R_c)
    elif rad_func_index == 2:
        rad_ij, drad_ij = rad_gaussian_cos(R_ij, eta_ijk, R_c)
        rad_ik, drad_ik = rad_gaussian_cos(R_ik, eta_ijk, R_c)

    # calculate angular function and its derivative
    cos_theta_ijk = ijk_6.repeat(n_parameters_ang).reshape((-1, n_parameters_ang))
    if ang_func_index == 0:
        ang_ijk, dang_ijk = ang_bump(cos_theta_ijk, lambda_ijk, xi_ijk)
    elif ang_func_index == 1:
        ang_ijk, dang_ijk = ang_cos(cos_theta_ijk, lambda_ijk, zeta_ijk, xi_ijk)
    elif ang_func_index == 2:
        ang_ijk, dang_ijk = ang_cos_int(cos_theta_ijk, lambda_ijk, zeta_ijk)

    # calculate unscaled angular eeACSFs
    x = elem_jk * rad_ij * rad_ik
    G_ang = np.sum(x * ang_ijk, axis=0)

    # calculate angular eeACSF derivatives
    if calc_derivatives:
        if scale_func_index == 0:
            dscale = dscale_crss(G_ang)
        elif scale_func_index == 1:
            dscale = dscale_linear(G_ang)
        elif scale_func_index == 2:
            dscale = dscale_sqrt(G_ang)
        y = dscale * elem_jk * ang_ijk
        z = np.ones((3, n_interactions, n_parameters_ang))
        a = ((dscale * x * dang_ijk) * z).T
        b = ((y * drad_ij * rad_ik) * z).T * dR_ij__dalpha_i_
        c = ((y * rad_ij * drad_ik) * z).T * dR_ik__dalpha_i_
        dG_ang__dalpha_i_ = np.sum(a * dcos_theta_ijk__dalpha_i_ + b + c, axis=1)
        dG_ang__dalpha_j_ = a * dcos_theta_ijk__dalpha_j_ - b
        dG_ang__dalpha_k_ = a * dcos_theta_ijk__dalpha_k_ - c

    # calculate angular eeACSFs
    if scale_func_index == 0:
        G_ang = scale_crss(G_ang)
    elif scale_func_index == 1:
        G_ang = scale_linear(G_ang)
    elif scale_func_index == 2:
        G_ang = scale_sqrt(G_ang)

    if not calc_derivatives:
        return G_ang, np.zeros((0, 3)), np.zeros((0, 0, 3)), np.zeros((0, 0, 3))

    return G_ang, dG_ang__dalpha_i_, dG_ang__dalpha_j_, dG_ang__dalpha_k_


####################################################################################################

@ncfjit
def elem_rad_eeACSF(elements_int_j, n_parameters_rad, H_parameters_rad, H_parameters_rad_scale,
                    n_interactions) -> NDArray:
    '''
    Return: H_j
    '''
    # determine element-dependent term
    H_j = np.zeros((n_interactions, n_parameters_rad), dtype=np.int64)
    for i in range(n_interactions):
        H_j[i] = H_parameters_rad[elements_int_j[i]]
    H_j = H_parameters_rad_scale * H_j

    return H_j


####################################################################################################

@ncfjit
def elem_rad_ACSF(elements_int_j, n_parameters_rad, element_types_rad, n_interactions) -> NDArray:
    '''
    Return: S_j
    '''
    # determine selection array of element contributions
    element_types_rad = element_types_rad.repeat(n_interactions).reshape((-1, n_interactions)).T
    elements_int_j = elements_int_j.repeat(n_parameters_rad).reshape((-1, n_parameters_rad))
    S_j = 1.0 * np.equal(element_types_rad, elements_int_j)

    return S_j


####################################################################################################

@ncfjit
def elem_rad_eeACSF_QMMM(elements_int_j, interaction_classes_j, atomic_charges_j, n_parameters_rad,
                         H_parameters_rad, H_parameters_rad_scale, n_interactions,
                         MM_atomic_charge_max) -> NDArray:
    '''
    Return: H_j
    '''
    # determine element-dependent term
    H_j = np.zeros((n_interactions, n_parameters_rad))
    for i in range(n_interactions):
        if interaction_classes_j[i] == 2:
            H_j[i] = (0.5 / MM_atomic_charge_max) * atomic_charges_j[i]
        else:
            H_j[i] = H_parameters_rad_scale * H_parameters_rad[elements_int_j[i]]

    return H_j


####################################################################################################

@ncfjit
def elem_ang_eeACSF(elements_int_j, elements_int_k, n_parameters_ang, H_parameters_ang,
                    H_parameters_ang_scale, H_type_jk, n_H_parameters, n_interactions) -> NDArray:
    '''
    Hint: Only contributions of angles ijk (not ikj) are taken into account.

    Return: H_jk
    '''
    # determine element-dependent term
    H_j = np.zeros((n_interactions, n_parameters_ang), dtype=np.int64)
    H_k = np.zeros((n_interactions, n_parameters_ang), dtype=np.int64)
    for i in range(n_interactions):
        H_j[i] = H_parameters_ang[elements_int_j[i]]
        H_k[i] = H_parameters_ang[elements_int_k[i]]
    factor = -2 * np.greater(H_type_jk, n_H_parameters) + 1
    bias = np.greater(H_type_jk, n_H_parameters)
    bias = bias.repeat(n_interactions).reshape((-1, n_interactions)).T
    bias = bias * (-1 * np.logical_and(np.equal(H_j, 0), np.equal(H_k, 0)) + 1)
    H_jk = np.absolute(H_j + factor * H_k) + bias
    H_jk = H_parameters_ang_scale * H_jk

    return H_jk


####################################################################################################

@ncfjit
def elem_ang_ACSF(elements_int_j, elements_int_k, n_parameters_ang, element_types_ang,
                  n_interactions) -> NDArray:
    '''
    Hint: Contributions of angles ijk and ikj are both taken into account.

    Return: S_jk
    '''
    # determine selection array of element contributions
    element_types_ang = element_types_ang.repeat(n_interactions).reshape((-1, n_interactions)).T
    elements_jk = 1000 * elements_int_j + elements_int_k
    elements_jk = elements_jk.repeat(n_parameters_ang).reshape((-1, n_parameters_ang))
    elements_kj = 1000 * elements_int_k + elements_int_j
    elements_kj = elements_kj.repeat(n_parameters_ang).reshape((-1, n_parameters_ang))
    S_jk = np.logical_or(np.equal(element_types_ang, elements_jk),
                         np.equal(element_types_ang, elements_kj))

    # take into account ijk and ikj
    S_jk = 2.0 * S_jk

    return S_jk


####################################################################################################

@ncfjit
def elem_ang_eeACSF_QMMM(elements_int_j, elements_int_k, interaction_classes_jk, atomic_charges_j,
                         atomic_charges_k, n_parameters_ang, H_parameters_ang,
                         H_parameters_ang_scale, H_type_jk, n_H_parameters, I_type_jk,
                         n_interactions, MM_atomic_charge_max) -> NDArray:
    '''
    Hint: Only contributions of angles ijk (not ikj) are taken into account.

    Return: H_jk
    '''
    # determine element-dependent term
    H_j = np.zeros((n_interactions, n_parameters_ang))
    H_k = np.zeros((n_interactions, n_parameters_ang))
    H_sign = np.ones((n_interactions, n_parameters_ang))
    for i in range(n_interactions):
        if interaction_classes_jk[i] == 2:
            H_j[i] = H_parameters_ang_scale * H_parameters_ang[elements_int_j[i]]
            H_k[i] = H_parameters_ang_scale * H_parameters_ang[elements_int_k[i]]
        elif interaction_classes_jk[i] == 3:
            if elements_int_j[i] >= 0:
                H_j[i] = (H_parameters_ang_scale * H_parameters_ang[elements_int_j[i]]
                          * atomic_charges_k[i] / MM_atomic_charge_max)
            else:
                H_j[i] = (H_parameters_ang_scale * H_parameters_ang[elements_int_k[i]]
                          * atomic_charges_j[i] / MM_atomic_charge_max)
            H_sign[i] = np.sign(H_j[i])
        else:
            H_j[i] = (0.5 / MM_atomic_charge_max**2) * atomic_charges_j[i] * atomic_charges_k[i]
            H_sign[i] = np.sign(H_j[i])
    factor = -2.0 * np.greater(H_type_jk, n_H_parameters) + 1.0
    bias = np.equal(I_type_jk, 0) * np.greater(H_type_jk, n_H_parameters) * H_parameters_ang_scale
    bias = bias.repeat(n_interactions).reshape((-1, n_interactions)).T
    bias = bias * (-1.0 * np.logical_and(np.equal(H_j, 0), np.equal(H_k, 0)) + 1.0)
    H_jk = H_sign * np.absolute(H_j + factor * H_k) + bias

    return H_jk


####################################################################################################

@ncfjit
def int_rad_eeACSF_QMMM(interaction_classes_j, I_type_j, n_parameters_rad, n_interactions) -> NDArray:
    '''
    Return: I_j
    '''
    # determine interaction-dependent term
    I_j = np.zeros((n_interactions, n_parameters_rad))
    A = np.equal(I_type_j, 0)
    B = np.equal(I_type_j, 1)
    for i in range(n_interactions):
        X = interaction_classes_j[i] == 1
        Y = interaction_classes_j[i] == 2
        I_j[i][A * X + B * Y] = 1.0

    return I_j


####################################################################################################

@ncfjit
def int_ang_eeACSF_QMMM(interaction_classes_jk, I_type_jk, n_parameters_ang, n_interactions) -> NDArray:
    '''
    Return: I_jk
    '''
    # determine interaction-dependent term
    I_jk = np.zeros((n_interactions, n_parameters_ang))
    A = np.equal(I_type_jk, 0)
    B = np.equal(I_type_jk, 1)
    C = np.equal(I_type_jk, 2)
    for i in range(n_interactions):
        X = interaction_classes_jk[i] == 2
        Y = interaction_classes_jk[i] == 3
        Z = interaction_classes_jk[i] == 4
        I_jk[i][A * X + B * Y + C * Z] = 1.0

    return I_jk


####################################################################################################

@ncfjit
def rad_bump(R, eta, R_c) -> Tuple[NDArray, NDArray]:
    '''
    Return: rad, drad
    '''
    # calculate bump combined radial and cutoff function and its derivative
    x = 1.0 - (R / R_c)**2
    rad = np.exp(eta - eta / x)
    drad = rad * ((-2.0 * eta / R_c**2) * R / x**2)

    return rad, drad


####################################################################################################

@ncfjit
def rad_gaussian_bump(R, eta, R_c) -> Tuple[NDArray, NDArray]:
    '''
    Return: rad, drad
    '''
    # calculate Gaussian radial function and its derivative
    e = np.exp(-eta * R**2)
    de_e = (-2.0 * eta) * R

    # calculate bump cutoff function and its derivative
    x = 1.0 - (R / R_c)**2
    b = np.exp(1.0 - 1.0 / x)
    db_b = (-2.0 / R_c**2) * R / x**2

    # calculate combined radial and cutoff function and its derivative
    rad = e * b
    drad = rad * (db_b + de_e)

    return rad, drad


####################################################################################################

@ncfjit
def rad_gaussian_cos(R, eta, R_c) -> Tuple[NDArray, NDArray]:
    '''
    Return: rad, drad
    '''
    # calculate Gaussian radial function and its derivative
    e = np.exp(-eta * R**2)
    de_e = (-2.0 * eta) * R

    # calculate cosine cutoff function and its derivative
    x = (pi / R_c) * R
    c = 0.5 + 0.5 * np.cos(x)
    dc = (-0.5 * pi / R_c) * np.sin(x)

    # calculate combined radial and cutoff function and its derivative
    rad = e * c
    drad = e * (dc + de_e * c)

    return rad, drad


####################################################################################################

@ncfjit
def ang_bump(cos_theta, lambda_ijk, xi_ijk) -> Tuple[NDArray, NDArray]:
    '''
    Return: ang, dang
    '''
    # calculate cosine angular function and its derivative
    x = lambda_ijk - (np.arccos(cos_theta) / pi)
    y = 1.0 - x**2
    ang = np.exp(xi_ijk - xi_ijk / y)
    dang = ang * ((-2.0 / pi) * xi_ijk) * x / y**2 / np.sqrt(1.0 - cos_theta**2)

    return ang, dang


####################################################################################################

@ncfjit
def ang_cos(cos_theta, lambda_ijk, zeta_ijk, xi_ijk) -> Tuple[NDArray, NDArray]:
    '''
    Return: ang, dang
    '''
    # calculate cosine angular function and its derivative
    theta = zeta_ijk * np.arccos(cos_theta)
    x = 0.5 + (0.5 * lambda_ijk) * np.cos(theta)
    ang = x**xi_ijk
    dang = (0.5 * lambda_ijk * zeta_ijk * xi_ijk) * ang / x * np.sin(theta) / np.sqrt(
        1.0 - cos_theta**2)

    return ang, dang


####################################################################################################

@ncfjit
def ang_cos_int(cos_theta, lambda_ijk, zeta_ijk) -> Tuple[NDArray, NDArray]:
    '''
    Return: ang, dang
    '''
    # calculate cosine angular function and its derivative
    x = 0.5 + (0.5 * lambda_ijk) * cos_theta
    ang = x**zeta_ijk
    dang = (0.5 * lambda_ijk * zeta_ijk) * ang / x

    return ang, dang


####################################################################################################

@ncfjit
def scale_crss(G) -> NDArray:
    '''
    Return: scale
    '''
    # calculate cube root-scaled-shifted scaling function
    return 3.0 * ((G + 1.0)**(1.0 / 3.0) - 1.0)


####################################################################################################

@ncfjit
def dscale_crss(G) -> NDArray:
    '''
    Return: dscale
    '''
    # calculate cube root-scaled-shifted scaling function derivative
    return (G + 1.0)**(-2.0 / 3.0)


####################################################################################################

@ncfjit
def scale_linear(G) -> NDArray:
    '''
    Return: scale
    '''
    # calculate linear scaling function
    return G


####################################################################################################

@ncfjit
def dscale_linear(G) -> NDArray:
    '''
    Return: dscale
    '''
    # calculate linear scaling function derivative
    return np.ones(G.shape)


####################################################################################################

@ncfjit
def scale_sqrt(G) -> NDArray:
    '''
    Return: scale
    '''
    # calculate square root scaling function
    return np.sqrt(G)


####################################################################################################

@ncfjit
def dscale_sqrt(G) -> NDArray:
    '''
    Return: dscale
    '''
    # calculate square root scaling function derivative
    dscale = np.zeros(G.shape)
    nonzero = G > 0.0
    dscale[nonzero] = 0.5 / np.sqrt(G[nonzero])

    return dscale


####################################################################################################

####################################################################################################

class Standardization(torch.nn.modules.module.Module):
    '''
    Standardization layer
    '''

####################################################################################################

    def __init__(self, features: int, device=None, dtype=None) -> None:
        '''
        Initialization
        '''
        # initialize parameters
        factory_kwargs = {'device': device, 'dtype': dtype}
        super().__init__()
        self.features = features
        self.weight = torch.nn.parameter.Parameter(torch.ones(features, **factory_kwargs))
        self.bias = torch.nn.parameter.Parameter(torch.zeros(features, **factory_kwargs))

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        '''
        Return: Standardization(input)
        '''
        return self.weight * (input - self.bias)


####################################################################################################

####################################################################################################

class sTanh(torch.nn.modules.module.Module):
    '''
    Scaled hyperbolic tangent
    '''

####################################################################################################

    def forward(self, input: Tensor) -> Tensor:
        '''
        Return: sTanh(input)
        '''
        return 1.59223 * torch.tanh(input)
