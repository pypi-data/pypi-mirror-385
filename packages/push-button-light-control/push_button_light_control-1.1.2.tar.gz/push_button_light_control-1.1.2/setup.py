'''
from setuptools import setup, find_packages
import os

# Read the long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="push-button-light-control",
    version="1.0.0",
    author="Basit Akram",
    author_email="basit.akramgaengineering.com",
    description="High-level API for Push Button Light Control devices with PIC24 microcontrollers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abdulbasit656/push-button-light-control",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
    keywords="push button, light control, led, serial, uart, protocol, pic24, automation, hardware",
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pb-light-demo=pb_api.examples.basic_usage:main',
            'pb-quick-start=pb_api.examples.quick_start:main',
        ],
    },
    include_package_data=True,
    project_urls={
        "Documentation": "https://github.com/abdulbasit656/push-button-light-control#readme",
        "Bug Reports": "https://github.com/abdulbasit656/push-button-light-control/issues",
        "Source": "https://github.com/abdulbasit656/push-button-light-control",
    },
)
'''


from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="push-button-light-control",
    version="1.1.2",
    author="Basit Akram",
    author_email="basit.akram@gaengineering.com",
    description="API for PIC24-based LED Controller devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyserial>=3.5",
    ],
    entry_points={
        'console_scripts': [
            'pb-api-demo=pb_api.examples.quick_start:main',
        ],
    },
)