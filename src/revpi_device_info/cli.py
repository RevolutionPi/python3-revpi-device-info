# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Copyright 2022-2023 KUNBUS GmbH

"""Hat EEPROM device info."""
__author__ = "Nicolai Buchwitz"
__copyright__ = "Copyright (C) 2023 KUNBUS GmbH"
__license__ = "MIT"

import argparse
from sys import stderr

from . import RevPiDeviceInfo
from .device_info import RevPiHatEEPROMException


def known_attributes():
    eeprom = RevPiDeviceInfo(load_contents=False)
    return list(filter(lambda x: not x.startswith("_"), vars(eeprom)))


def output_json(device_info: RevPiDeviceInfo, attributes: list[str]):
    print(device_info.to_json(attributes))


def line(length: int):
    return "-" * length


def output_text(device_info: RevPiDeviceInfo, line_length: int = 60):
    print(line(line_length))
    print("Product".center(line_length))
    print(line(line_length))
    print(f"Vendor:\t\t{device_info.vendor}")
    print(f"Product:\t{device_info.product}")
    print(f"Version:\t{device_info.product_version}")
    print(f"Data Version:\t{device_info.eeprom_data_version}", end="")
    if device_info.eeprom_data_version <= 0:
        print(" (WARNING: THIS IS A DEVELOPMENT VERSION)", end="")
    print()
    print(f"Id:\t\t{device_info.product_id_revision}")

    print()
    print(line(line_length))
    print("Device".center(line_length))
    print(line(line_length))
    print(f"Serial:\t\t{device_info.serial}")
    print(f"First MAC:\t{device_info.first_mac_address}")
    print(f"EOL Date:\t{device_info.eol_date}")
    print(f"Batch / Lot:\t{device_info.batch_number}")

    print()
    print(line(line_length))
    print("RevPi HAT EEPROM".center(line_length))
    print(line(line_length))
    print(f"UUID:\t\t{device_info.uuid}")
    print(f"Format Version:\t{device_info.format_version}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Human readable RevPi Device Info",
    )

    parser.add_argument(
        "-p", "--hat-path",
        type=str,
        required=False,
        default="/proc/device-tree/hat/",
        help='Override path to HAT files',
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
        default=None, help="Filter JSON output for only specific attributes",
    )

    args = parser.parse_args()

    try:
        device_info = RevPiDeviceInfo(hat_path=args.hat_path)
    except RevPiHatEEPROMException as e:
        print(f"An error occurred while reading the HAT contents: {e}", file=stderr)
        return 1

    if args.json:
        output_json(device_info, args.attributes)
    else:
        output_text(device_info)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
