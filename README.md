<details>
<summary>We have moved to GitLab! Read this for more information.</summary>

We have recently moved our repositories to GitLab. You can find python3-revpi-device-info
here: https://gitlab.com/revolutionpi/python3-revpi-device-info  
All repositories on GitHub will stay up-to-date by being synchronised from
GitLab.

We still maintain a presence on GitHub but our work happens over at GitLab. If
you want to contribute to any of our projects we would prefer this contribution
to happen on GitLab, but we also still accept contributions on GitHub if you
prefer that.
</details>

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
