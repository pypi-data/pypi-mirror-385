# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import importlib
import pkgutil
from flask import Blueprint

bp = Blueprint("frontend", __name__)


def _load_controllers() -> None:
    """
    Load compliant with mypy...
    """
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module_name}")


_load_controllers()
