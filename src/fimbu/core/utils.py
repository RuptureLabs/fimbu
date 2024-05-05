from __future__ import annotations 
from typing import TYPE_CHECKING, Tuple

import configparser
import os

if TYPE_CHECKING:
    from pydantic import BaseModel, Field


def load_init_settings() -> configparser.ConfigParser:
    """
    This is used the first time settings are needed, if the user hasn't
    configured settings manually.
    """
    config = configparser.ConfigParser()
    path = os.path.join(os.curdir, "fimbu.ini")

    if os.path.exists(path):
        config.read(path)
    else:
        config['default'] = {
            'settings': 'fimbu.conf.global_settings',
        }
    return config


def is_fimbu_project() -> bool:
    """A fimbu project is specified by having fimbu.ini in the current directory"""
    return os.path.exists(os.path.join(os.curdir, 'fimbu.ini'))


def setup_fimbu():
    """
    This is used the first time settings are needed, if the user hasn't
    configured settings manually.
    """
    config = load_init_settings()
    os.environ.setdefault('FIMBU_SETTINGS_MODULE', config['default']['settings'])
    
    if is_fimbu_project():
        import sys
        sys.path.append(os.path.abspath(os.curdir))


def get_pydantic_fields(model: BaseModel) -> Tuple[dict[str, Field], dict[str, Field]]:
    """
    Get the fields from a pydantic model.

    Args:
        model: A pydantic model
    Returns:
        A tuple of (required_fields, optionnal_fields)

    """
    fields = model.model_fields
    required_fields = {}
    optionnal_fields = {}

    for field_name, field in fields.items():
        if field.is_required():
            required_fields[field_name] = field
        else:
            optionnal_fields[field_name] = field
    return required_fields, optionnal_fields
