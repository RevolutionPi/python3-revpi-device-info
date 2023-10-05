# -*- coding: utf-8 -*-
"""Setup-script for revpi-device-info."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 KUNBUS GmbH"
__license__ = "MIT"

from setuptools import find_namespace_packages, setup

from src.revpi_device_info.__about__ import __version__

with open("README.md") as fh:
    # Load long description from readme file
    long_description = fh.read()

setup(
    name="revpi_device_info",
    version=__version__,
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">= 3.6",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "revpi-device-info = revpi_device_info.cli:main",
        ]
    },
    platforms=["revolution pi"],
    url="https://github.com/RevolutionPi/python3-revpi-device-info",
    license="LGPLv2",
    author="Nicolai Buchwitz",
    author_email="n.buchwitz@kunbus.com",
    description="RevPi device information from RevPi HAT EEPROM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["revpi", "revolution pi", "revpimodio", "plc", "automation"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
