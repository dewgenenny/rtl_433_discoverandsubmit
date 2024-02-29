from setuptools import setup, find_packages
import os

# Read the content of README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="rtl_433_discoverandsubmit",
    version="0.1.9",
    packages=find_packages(),
    install_requires=[
        "paho-mqtt",
        "uni-curses"
    ],

    # Metadata
    author="Tom George",
    author_email="tom@penberth.com",
    description="A small command line utility to connect to an MQTT server, listen to rtl_433 events and allow a user to generate auto-discovery config for home assistant for the devices they choose",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT",  # Assuming you want to use the MIT License
    keywords="rtl_433 mqtt homeassistant",
    package_data={
        'rtl_433_discoverandsubmit': ['config/*.json'],
    },
    # Entry points
    entry_points={
        'console_scripts': [
            'rtl_433_discoverandsubmit=rtl_433_discoverandsubmit.modules.cli_interface:main',
        ],
    },
)

