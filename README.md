# python3-revpi-device-info

Python3 library to interfact with RevPi device information

## Example usage

```python

import revpi_device_info

# initialize EEPROM and load contents from default path (/proc/device-tree/hat)
try:
    device = revpi_device_info.RevPiDeviceInfo()

    # print product name
    print(device.product)
except revpi_device_info.RevPiHatEEPROMAttributeException as e:
    print(f"An error occured while reading the HAT files: {e}")

```