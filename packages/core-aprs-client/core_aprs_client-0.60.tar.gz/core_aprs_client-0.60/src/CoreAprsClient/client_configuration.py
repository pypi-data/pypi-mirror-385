#
# Core APRS Client
# Configuration file import and validation
# Imports the configuration data into a dictionary object
# and performs a generic validation against predefined schema data
# Author: Joerg Schultze-Lutter, 2025
#
# aprslib does not allow us to pass additional parameters to its
# callback function. Therefore, this module acts as a pseudo object in
# order to encapsulate the client configuration data
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
import configparser
from os import path
from .client_configuration_schema import (
    CONFIGURATION_SCHEMA,
    EXCLUDED_CONFIGURATION_SCHEMA,
)

config = configparser.ConfigParser()
program_config = {}


def load_config(config_file: str):
    """
    Loads the program configuration from the config file
    Returns the program configuration as a dictionary
    If the config file does not exist, the dictionary will be empty

    Parameters
    ==========
    config_file: 'str'
        Name of the configuration file

    Returns
    =======
    none
    """

    if path.isfile(config_file):
        try:
            config.read(config_file)
            config_to_dict(config)
        except:
            program_config.clear()
    else:
        program_config.clear()
    validate_config_schema(program_config)


def _parse_value(value: str):
    """
    Helper method to convert a string to its native value format

    Parameters
    ==========
    value: 'str'
       Our input value

    Returns
    =======
    Converted data type
    """
    if value.lower() in {"true", "yes", "on"}:
        return True
    elif value.lower() in {"false", "no", "off"}:
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def config_to_dict(myconfig: configparser.ConfigParser):
    """
    Converts a ConfigParser object to a dictionary

    Parameters
    ==========
    myconfig: configparser.ConfigParser
       ConfigParser input object

    Returns
    =======
    program_config: dict
        Our program configuration dictionary
    """
    program_config.clear()
    for section in myconfig.sections():
        program_config[section] = {
            key: _parse_value(value) for key, value in config.items(section)
        }
    return program_config


def get_config():
    """
    Helper method: gets the program configuration dictionary

    Parameters
    ==========

    Returns
    =======
    program_config: 'dict'
        Our program configuration dictionary
    """
    return program_config


def validate_config_schema(cfg: dict):
    """
    Helper method: validates config file data against
    predefined schema and checks for missing fields and/or
    fields with invalid data types

    Parameters
    ==========
    cfg: dict
        Dictionary with data from config file

    Returns
    =======
    """
    for section, values in cfg.items():
        if not section.startswith("coac_"):
            continue

        expected_schema = CONFIGURATION_SCHEMA.get(section)
        if not expected_schema:
            if section in EXCLUDED_CONFIGURATION_SCHEMA:
                continue
            else:
                raise KeyError(
                    f"Schema definition for section '{section}' is missing from the configuration file"
                )

        # a) Check all required keys are present
        missing_keys = set(expected_schema.keys()) - set(values.keys())
        if missing_keys:
            raise KeyError(
                f"Configuration file section '{section}': missing keys {missing_keys}"
            )

        # b) Check type correctness
        for key, expected_type in expected_schema.items():
            if key not in values:
                continue
            actual_value = values[key]
            if not isinstance(actual_value, expected_type):
                raise TypeError(
                    f"Configuration file section '{section}': key '{key}' has wrong type "
                    f"(expected {expected_type.__name__}, got {type(actual_value).__name__})"
                )


if __name__ == "__main__":
    pass
