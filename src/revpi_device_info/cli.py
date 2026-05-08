# SPDX-FileCopyrightText: 2022-2023 KUNBUS GmbH
#
# SPDX-License-Identifier: MIT

"""Hat EEPROM device info."""

__author__ = "Nicolai Buchwitz"
__copyright__ = "Copyright (C) 2023 KUNBUS GmbH"
__license__ = "MIT"

import argparse
import logging
from sys import stderr
from typing import Union

from . import RevPiDeviceInfo, RevPiHatEEPROMException


def known_attributes() -> list[str]:
    """Return a list of known attributes of RevPiDeviceInfo."""
    eeprom = RevPiDeviceInfo(load_contents=False)
    return list(filter(lambda x: not x.startswith("_"), vars(eeprom)))


def output_json(device_info: RevPiDeviceInfo, attributes: list[str]) -> None:
    """Write RevPi Device Info to stdout as JSON."""
    print(device_info.to_json(attributes))


def line(length: int) -> str:
    """Create a line of dashes."""
    return "-" * length


def none_to_string(value: Union[None, int, float, str]) -> str:
    """Convert None to empty string."""
    return str(value) if value is not None else "-> Only available on devices with HAT EEPROM"


def output_text(device_info: RevPiDeviceInfo, line_length: int = 60) -> None:
    """Write RevPi Device Info to stdout."""
    print(line(line_length))
    print("Product".center(line_length))
    print(line(line_length))
    print(f"Vendor:\t\t{none_to_string(device_info.vendor)}")
    print(f"Product:\t{none_to_string(device_info.product)}")
    print(f"Version:\t{none_to_string(device_info.product_version)}")
    print(f"Data Version:\t{none_to_string(device_info.eeprom_data_version)}", end="")
    if device_info.eeprom_data_version is not None and device_info.eeprom_data_version <= 0:
        print(" (WARNING: THIS IS A DEVELOPMENT VERSION)", end="")
    print()
    print(f"Id:\t\t{none_to_string(device_info.product_id_revision)}")

    print()
    print(line(line_length))
    print("Device".center(line_length))
    print(line(line_length))
    print(f"Serial:\t\t{none_to_string(device_info.serial)}")
    print(f"First MAC:\t{none_to_string(device_info.first_mac_address)}")
    print(f"Architecture:\t{none_to_string(device_info.architecture)}")
    print(f"OS Version:\t{none_to_string(device_info.os_version)}")
    print(f"Test Date:\t{none_to_string(device_info.eol_date)}")
    print(f"Batch / Lot:\t{none_to_string(device_info.batch_number)}")

    print()
    print(line(line_length))
    print("RevPi HAT EEPROM".center(line_length))
    print(line(line_length))
    print(f"UUID:\t\t{none_to_string(device_info.uuid)}")
    print(f"Format Version:\t{none_to_string(device_info.format_version)}")


def main() -> int:
    """Start the main entry point of CLI."""
    parser = argparse.ArgumentParser(
        description="Human readable RevPi Device Info",
    )

    parser.add_argument(
        "-p",
        "--hat-path",
        type=str,
        required=False,
        default="/proc/device-tree/hat/",
        help="Override path to HAT EEPROM path",
    )

    parser.add_argument(
        "--json",
        required=False,
        action="store_true",
        default=False,
        help="Output JSON instead of text",
    )

    parser.add_argument(
        "-a",
        dest="attributes",
        type=str,
        action="append",
        choices=known_attributes(),
        default=None,
        help="Filter JSON output for only specific attributes",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbose",
        default=0,
        help="switch on verbose logging",
    )

    args = parser.parse_args()

    logging.basicConfig(
        format="{asctime} [{levelname:8}] {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
        stream=stderr,
        level=logging.WARNING - 10 * min(args.verbose, 3),
    )

    try:
        device_info = RevPiDeviceInfo(hat_path=args.hat_path)
    except RevPiHatEEPROMException as e:
        print(f"An error occurred while reading the device info contents: {e}", file=stderr)
        return 1

    if args.json:
        output_json(device_info, args.attributes)
    else:
        output_text(device_info)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
