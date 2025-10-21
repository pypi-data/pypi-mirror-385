#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__copyright__ = """ This code is licensed under the 3-clause BSD license.
Copyright ETH Zurich, Department of Chemistry and Applied Biosciences, Reiher Group.
See LICENSE.txt for details.
"""

import scine_utilities as utils

from ._version import __version__  # noqa: F401
from .module import ParrotModule

# Load module into manager singleton upon initialization
module_manager = utils.core.ModuleManager.get_instance()   # type: ignore
parrot = ParrotModule()
module_manager.load_module(parrot)
