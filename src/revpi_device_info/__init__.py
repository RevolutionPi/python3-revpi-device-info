# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Copyright 2022-2023 KUNBUS GmbH

"""Hat EEPROM device info."""
from .__about__ import __author__, __copyright__, __license__, __version__  # noqa: F401
from .device_info import RevPiDeviceInfo, RevPiHatEEPROMException

__all__ = ["RevPiDeviceInfo", "RevPiHatEEPROMException"]
