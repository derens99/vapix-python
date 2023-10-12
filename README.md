# Vapix API Python Wrapper by Axis Communications

This Python library provides a seamless wrapper around the Vapix API by Axis Communications, facilitating effortless interactions with all their  cameras.

## Features

- Complete Pythonic access to all Vapix API endpoints.
- Simplified methods for interacting with all cameras.
- Built with extensibility and ease-of-use in mind.

## Installation

To install the wrapper, you can use pip: 

TODO - PyPi hosting coming soon

## Quick Start

```python
from vapix_python.VapixAPI import VapixAPI

# Initialize the API caller with the base URL
vapix_api = VapixAPI(os.environ.get('host'), os.environ.get('user'), os.environ.get('password'))

print(vapix_api.ptz.get_current_ptz())
```