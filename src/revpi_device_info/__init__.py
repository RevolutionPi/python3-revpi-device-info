# SPDX-FileCopyrightText: 2023 KUNBUS GmbH
#
# SPDX-License-Identifier: MIT

"""Hat EEPROM device info."""
from .__about__ import __author__, __copyright__, __license__, __version__  # noqa: F401
from .device_info import RevPiDeviceInfo, RevPiHatEEPROMException

__all__ = ["RevPiDeviceInfo", "RevPiHatEEPROMException"]
