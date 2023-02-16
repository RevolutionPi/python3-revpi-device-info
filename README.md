# python3-revpi-device-info

Python3 library to interact with RevPi device information.

## Example usage

```python

import revpi_device_info

# initialize EEPROM and load contents from default path (/proc/device-tree/hat)
try:
    device = revpi_device_info.RevPiDeviceInfo()

    # print product name
    print(device.product)
except revpi_device_info.RevPiHatEEPROMException as e:
    print(f"An error occurred while reading the HAT files: {e}")

```
