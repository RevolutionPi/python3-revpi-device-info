# SPDX-FileCopyrightText: 2022-2023 KUNBUS GmbH
#
# SPDX-License-Identifier: MIT

"""Hat EEPROM device info."""

__author__ = "Nicolai Buchwitz"
__copyright__ = "Copyright (C) 2023 KUNBUS GmbH"
__license__ = "MIT"

import json
import os.path
import platform
from datetime import date
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class RevPiHatEEPROMException(Exception):
    """Exception base of this module."""

    pass


class RevPiHatEEPROMAttributeException(RevPiHatEEPROMException):
    """Exception raised when HAT EEPROM attribute could not be read."""

    pass


class RevPiHatEEPROMPathException(RevPiHatEEPROMException):
    """Exception raised when HAT EEPROM path does not exist."""

    pass


class RevPiDeviceInfoException(RevPiHatEEPROMException):
    """Exception raised when device info could not be read."""

    pass


class RevPiSystemInfoException(RevPiHatEEPROMException):
    """Exception raised when system info could not be read."""

    pass


class RevPiDeviceInfo:
    """
    Represents device information for a Revolution Pi (RevPi).

    The class provides utilities for reading RevPi-specific hardware and software
    information, including attributes stored in the RevPi HAT EEPROM and system files.
    It allows for loading device-specific data, accessing raw attributes, and exporting
    data to JSON format.

    Attributes
    ----------
    uuid:
        UUID of the RevPi device.
    format_version:
        Format version of the HAT EEPROM data.
    eeprom_data_version:
        Data version of the HAT EEPROM.
    vendor:
        Vendor name as specified in the HAT EEPROM file.
    product:
        Product name as specified in the HAT EEPROM file.
    product_id:
        Product ID derived from HAT EEPROM file and base offset.
    product_id_revision:
        Product ID with revision ("PR<id>R<rev>").
    product_revision:
        Revision number of the product.
    product_version:
        Version of the product (major.minor).
    product_version_major:
        Major version of the product.
    product_version_minor:
        Minor version of the product.
    serial:
        Serial number of the RevPi device.
    eol_date:
        End-of-line date for the device.
    batch_number:
        Batch number of the device.
    first_mac_address:
        First MAC address associated with the device.
    architecture:
        System architecture as identified by the platform.
    os_version:
        Operating system version.
    """

    PRODUCT_ID_BASE = 100000

    def __init__(
        self,
        load_contents: bool = True,
        hat_path: str = "/proc/device-tree/hat",
        devinfo_path: str = "/usr/share/revpi/devinfo",
        os_release_path: str = "/etc/os-release",
    ) -> None:
        """
        Create a new instance of RevPiDeviceInfo.

        Parameters
        ----------
        load_contents:
            Populate class with data from RevPi Hat EEPROM
        hat_path:
            Path to HAT EEPROM files
        devinfo_path:
            Path to devinfo files
        os_release_path:
            Path to os-release file
        """
        self._hat_path = hat_path
        self._devinfo_path = devinfo_path
        self._os_release_path = os_release_path
        """Path to os-release file."""

        self.uuid: Optional[str] = None
        self.format_version: Optional[int] = None
        self.eeprom_data_version: Optional[int] = None

        self.vendor: Optional[str] = None
        self.product: Optional[str] = None
        self.product_id: Optional[int] = None
        self.product_id_revision: Optional[str] = None
        self.product_revision: Optional[int] = None
        self.product_version: Optional[str] = None
        self.product_version_major: Optional[int] = None
        self.product_version_minor: Optional[int] = None

        self.serial: Optional[int] = None
        self.eol_date: Optional[date] = None
        self.batch_number: Optional[int] = None
        self.first_mac_address: Optional[str] = None
        self.architecture: Optional[str] = None
        self.os_version: Optional[str] = None

        self._os_release: Dict[str, str] = {}
        """Dictionary of key-value pairs from os-release file."""
        self._raw_values = {}

        if load_contents:
            self.load()

    def load(self) -> None:
        """Load values from RevPi HAT EEPROM or system info."""
        try:
            logger.debug("Loading system info from %s", self._os_release_path)
            self._load_system_info()
        except RevPiSystemInfoException as e:
            logger.warning("Could not load system info: %s", e)

        if os.path.exists(self._hat_path):
            logger.info("Loading HAT EEPROM information from %s", self._hat_path)
            # This RevPi has a HAT EEPROM device
            self._load_hat_info()
        else:
            # Fallback to /usr/share/revpi/devinfo information
            logger.info("Loading device info from %s (no HAT EEPROM available)", self._devinfo_path)
            self._load_device_info()

    def _load_system_info(self) -> None:
        if not os.path.exists(self._os_release_path):
            raise RevPiSystemInfoException(f"os-release path '{self._os_release_path}' does not exist")

        try:
            # Read os-release file and parse key-value pairs for self._os_release dict
            with open(self._os_release_path, "r") as fh:
                for line in fh:
                    key_value = line.split("=", 1)
                    if len(key_value) != 2:
                        continue

                    key, value = key_value
                    # Use upper case keys to avoid case sensitivity issues
                    key = key.strip().upper()
                    # Remove surrounding quotes and whitespace in value
                    value = value.strip(" \t\n\r'\"")

                    self._os_release[key] = value

            logger.debug("Loaded %s key-value pairs from os-release file", len(self._os_release))

        except Exception as e:
            raise RevPiSystemInfoException(f"Could not read os-release file. {e}") from e

        self.architecture = platform.machine()
        self.os_version = self._os_release.get("PRETTY_NAME")

    def _load_hat_info(self) -> None:
        if not os.path.exists(self._hat_path):
            raise RevPiHatEEPROMPathException(f"HAT EEPROM path '{self._hat_path}' does not exist")

        self.uuid = self._hat_attribute("uuid")
        self.format_version = self._hat_attribute_int("custom_0")
        self.eeprom_data_version = self._hat_attribute_int("custom_6")

        self.vendor = self._hat_attribute("vendor")
        self.product = self._hat_attribute("product")
        self.product_id = self._hat_attribute_int("product_id") + self.PRODUCT_ID_BASE
        self.product_revision = self._hat_attribute_int("custom_2")
        self.product_version = self._hat_attribute_version("product_ver")
        self.product_version_major = self._version_major(self.product_version)
        self.product_version_minor = self._version_minor(self.product_version)
        self.product_id_revision = f"PR{self.product_id}R{self.product_revision:02}"

        self.serial = int(self._hat_attribute("custom_1"))
        self.eol_date = self._hat_attribute_date("custom_3")
        self.batch_number = self._hat_attribute_int("custom_4")
        self.first_mac_address = self._hat_attribute("custom_5")

    def _load_device_info(self) -> None:
        """
        Load device information from the device info directory.

        Raises
        ------
        RevPiDeviceInfoException:
            If the devinfo path does not exist, or if the attributes cannot be loaded.
        """
        if not os.path.exists(self._devinfo_path):
            raise RevPiDeviceInfoException(f"devinfo path '{self._devinfo_path}' does not exist")

        try:
            self.serial = int(self._device_info_attribute("serial-number"))
        except (RevPiDeviceInfoException, ValueError) as e:
            logger.warning("Could not load serial number: %s", e)

        try:
            self.first_mac_address = self._device_info_attribute("base-mac-address")
        except RevPiDeviceInfoException as e:
            logger.warning("Could not load base MAC address: %s", e)

    def _device_info_attribute(self, name: str) -> str:
        """
        Read attribute from /usr/share/revpi/devinfo.

        An attribute is the file name in the devinfo directory.

        Parameters
        ----------
        name: str
            Name of the attribute (file) to read.

        Returns
        -------
        str:
            Stripped content of the attribute file.

        Raises
        ------
        RevPiDeviceInfoException:
            If the attribute file cannot be read.
        """
        path = os.path.join(self._devinfo_path, name)

        try:
            with open(path, "r") as fh:
                return fh.read().strip()
        except OSError as e:
            raise RevPiDeviceInfoException(f"Could not read 'devinfo' file {name}. {e}") from e

    def _version_major(self, version: str) -> int:
        major, _ = version.split(".")

        return int(major)

    def _version_minor(self, version: str) -> int:
        _, minor = version.split(".")

        return int(minor)

    def _hat_attribute_version(self, name: str) -> str:
        value = self._hat_attribute_int(name)

        major = int(value / 100)
        minor = int(value % 100)

        version = f"{major}.{minor}"

        return version

    def _hat_attribute_date(self, name: str) -> date:
        value = self._hat_attribute(name)

        return date.fromisoformat(value)

    def _hat_attribute_int(self, name: str) -> int:
        value = int(self._hat_attribute(name), base=16)

        self._raw_values[name] = value

        return value

    def _hat_attribute(self, name: str) -> str:
        path = os.path.join(self._hat_path, name)

        try:
            with open(path, "r") as fh:
                value = fh.read().rstrip("\x00")
        except Exception as e:
            raise RevPiHatEEPROMAttributeException(f"Could not read HAT EEPROM value for {name}. {e}") from e

        # override raw value with parsed int value
        self._raw_values[name] = value

        return value

    def raw_values(self) -> dict:
        """
        Get dict of (mostly) raw attributes. Only integer conversion is done to attributes where necessary.

        Return
        ------
        dict:
            raw attributes from the HAT EEPROM files
        """
        return self._raw_values

    def to_json(self, attributes: list[str] = None) -> str:
        """
        JSON encoded attributes of the RevPi Device Infos.

        Parameters
        ----------
        attributes:
            Optional list with attributes to filter

        Return
        ------
        str:
            JSON string with all / filtered attributes
        """
        output = {}

        for attribute in filter(lambda x: not x.startswith("_"), vars(self)):
            if attributes is not None and attribute not in attributes:
                continue

            output[attribute] = getattr(self, attribute)

        return json.dumps(output, default=str)
