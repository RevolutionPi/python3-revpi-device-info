from setuptools import setup, find_packages


setup(
    name='RevPi Device Info',
    version='1.0',
    author="Nicolai Buchwitz",
    author_email="n.buchwitz@kunbus.com",
    description='RevPi device information from RevPi HAT EEPROM',
    url='https://github.com/RevolutionPi/python3-revpi-device-info',
    packages=find_packages(),
    entry_points={'console_scripts': ['revpi-device-info = revpi_device_info.__main__:main']}
)
