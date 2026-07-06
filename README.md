# vapix-python

A Python wrapper for the [VAPIX API](https://developer.axis.com/vapix/) by Axis Communications, providing a clean, typed interface for controlling Axis network cameras.

## Features

- **PTZ control** — absolute, relative, and continuous pan/tilt/zoom moves, focus, iris, brightness, presets, and home position via `com/ptz.cgi`.
- **Geolocation** — read and set the camera's configured position and heading.
- **Device parameters** — list device parameters via `param.cgi`.
- **Solid HTTP layer** — one authenticated session (digest or basic auth), HTTP or HTTPS, real per-request timeouts, and typed exceptions (`VapixAuthenticationError`, `VapixRequestError`, `VapixResponseError`).
- **Typed and tested** — full type hints and a mocked test suite that runs without camera hardware.

## Installation

Not yet published to PyPI. Install from source:

```bash
pip install git+https://github.com/derens99/vapix-python.git
```

Or for local development (using [uv](https://docs.astral.sh/uv/)):

```bash
git clone https://github.com/derens99/vapix-python.git
cd vapix-python
uv sync
```

## Quick start

```python
from vapix_python import VapixAPI

with VapixAPI("192.168.0.90", "root", "your-password") as api:
    # Current pan/tilt/zoom
    pan, tilt, zoom = api.ptz.get_current_position()

    # Move the camera
    api.ptz.absolute_move(pan=90, tilt=0, zoom=500, speed=50)
    api.ptz.go_home(speed=100)

    # Geolocation
    position = api.geolocation.get_position()
    print(position["lat"], position["lon"])

    # Device parameters
    brand = api.get_parameters(group="Brand")
```

### Connection options

```python
api = VapixAPI(
    "cam.example.com",
    "root",
    "your-password",
    timeout=10,          # per-request timeout in seconds
    secure=True,         # use HTTPS
    verify_ssl=False,    # or a path to a CA bundle
    auth_method="digest" # or "basic"
)
```

### Error handling

```python
from vapix_python import VapixAPI, VapixAuthenticationError, VapixRequestError

try:
    with VapixAPI("192.168.0.90", "root", "wrong") as api:
        api.ptz.get_current_position()
except VapixAuthenticationError:
    print("Bad credentials")
except VapixRequestError as exc:
    print(f"Camera unreachable or returned an error: {exc}")
```

## Development

The project uses [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
uv sync               # create .venv and install the package + dev dependencies
uv run ruff check .   # lint
uv run pytest         # run the test suite (no camera required)
uv build              # build sdist and wheel
```

`pip install -e ".[dev]"` also works if you prefer plain pip.

## Migrating from 0.1.x

The old CamelCase module paths still work but emit a `DeprecationWarning`:

```python
from vapix_python.VapixAPI import VapixAPI   # deprecated
from vapix_python import VapixAPI            # preferred
```

Notable fixes in 0.2.0:

- Request timeouts are now actually applied (previously the `timeout` argument was silently ignored).
- `PTZControl.rename_preset_number(number, name)` now sends the number and name in the correct fields (they were swapped).
- Geolocation responses are parsed robustly (namespaced XML supported, no stray `print()` output) and camera-reported errors raise `VapixResponseError`.
