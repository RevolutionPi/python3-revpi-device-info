# -*- coding: utf-8 -*-
"""Hat EEPROM device info."""
__author__ = "Nicolai Buchwitz"
__copyright__ = "Copyright (C) 2023 KUNBUS GmbH"
__license__ = "MIT"

import json
import os.path
from datetime import date


class RevPiHatEEPROMException(Exception):
    """Exception base of this module."""
    pass


class RevPiHatEEPROMAttributeException(RevPiHatEEPROMException):
    pass


class RevPiHatEEPROMPathException(RevPiHatEEPROMException):
    pass


class RevPiDeviceInfo:
    PRODUCT_ID_BASE = 100000

    def __init__(self, load_contents: bool = True, hat_path: str = "/proc/device-tree/hat/") -> None:
        """
        Create new instance of RevPiDeviceInfo.

        :param bool load_contents: Populate class with data from RevPi Hat EEPROM
        :param str hat_path: Path to HAT files
        """
        self._hat_path = hat_path

        self.uuid: str = None
        self.format_version: int = None
        self.eeprom_data_version: int = None

        self.vendor: str = None
        self.product: str = None
        self.product_id: int = None
        self.product_id_revision: str = None
        self.product_revision: int = None
        self.product_version: str = None
        self.product_version_major: int = None
        self.product_version_minor: int = None

        self.serial: int = None
        self.eol_date: date = None
        self.batch_number: int = None
        self.first_mac_address: str = None

        self._raw_values = {}

        if load_contents:
            self.load()

    def load(self):
        """
        Load values from RevPi HAT EEPROM
        :raises: RevPiHatEEPROMAttributeException: if the attribute cannot be read from HAT files
        """

        if not os.path.exists(self._hat_path):
            raise RevPiHatEEPROMPathException("HAT EEPROM path does not exists")

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
        path = f"{self._hat_path}/{name}"

        try:
            with open(path, "r") as fh:
                value = fh.read().rstrip('\x00')
        except Exception as e:
            raise RevPiHatEEPROMAttributeException(
                f"Could not read HAT value for {name}. {e}")

        # override raw value with parsed int value
        self._raw_values[name] = value

        return value

    def raw_values(self) -> dict:
        """
        Get dict of (mostly) raw attributes. Only integer conversion is done to attributes where necessary
        :return: raw attributes from the HAT files
        :rtype: dict
        """
        return self._raw_values

    def to_json(self, attributes: list[str] = None) -> str:
        """
        JSON encoded attributes of the RevPi Device Infos

        :param attributes: Optional list with attributes to filter
        :return: JSON string with all / filtered attributes
        :rtype: str
        """
        output = {}

        for attribute in filter(lambda x: not x.startswith("_"), vars(self)):
            if attributes is not None and attribute not in attributes:
                continue

            output[attribute] = getattr(self, attribute)

        return json.dumps(output, default=str)
