# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask import current_app, flash


def init_flash() -> None:
    """
    Initialize flash messages.
    """
    if current_app.config.get('INIT_ERROR'):
        flash(current_app.config['INIT_ERROR'], 'error')


def byte_to_gi(bytes_value: float, suffix: str = 'B') -> str:
    """
    Convert in human readable units.

    Args:
        bytes_value (integer): Value not human readable.
        suffix (str): Suffix for value given to (default: B).

    Returns:
        str: human readable value in Gi.
    """
    gib = bytes_value / (1024**3)
    return f"{gib:.1f}Gi{suffix}"
