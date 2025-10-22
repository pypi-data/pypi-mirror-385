# LocalCartesian

Fast GPS to local Cartesian coordinate conversion using GeographicLib.

## Description

This package provides efficient conversion between GPS coordinates (latitude, longitude) and local Cartesian coordinates (x, y). It uses the GeographicLib C++ library through Python bindings created with pybind11.

The package exists because GeographicLib's Python bindings don't include the equivalent of the C++ `LocalCartesian` class, which is essential for many geospatial applications.

## Installation

Install from PyPI using [uv](https://docs.astral.sh/uv/):
```bash
uv add localcartesian
```
or via pip globally, or inside any Python environment like virtualenv or conda:
```bash
pip install localcartesian
```

## Usage

```python
import numpy as np
from localcartesian import gps2xy, xy2gps

# Define some GPS coordinates (lat, lon pairs)
gps_coords = [
    [40.7128, -74.0060],  # New York City
    [40.7589, -73.9851],  # Times Square
    [40.6892, -74.0445],  # Statue of Liberty
]

# Define origin point (lat, lon, altitude)
origin = [40.7128, -74.0060, 0.0]  # NYC as origin

# Convert GPS to local Cartesian coordinates
local_coords = gps2xy(gps_coords, origin)
print("Local coordinates:", local_coords)

# Convert back to GPS coordinates
gps_back = xy2gps(local_coords, origin)
print("GPS coordinates:", gps_back)
```

## API Reference

### `gps2xy(latlon, origin_latlonalt)`

Convert GPS coordinates to local Cartesian coordinates.

**Parameters:**
- `latlon`: List of [latitude, longitude] pairs
- `origin_latlonalt`: Origin point as [latitude, longitude, altitude]

**Returns:**
- List of [x, y] coordinate pairs in meters

### `xy2gps(xy, origin_latlonalt)`

Convert local Cartesian coordinates to GPS coordinates.

**Parameters:**
- `xy`: List of [x, y] coordinate pairs in meters
- `origin_latlonalt`: Origin point as [latitude, longitude, altitude]

**Returns:**
- List of [latitude, longitude] pairs

## Development

### Building from Source Locally

Clone the repository and navigate to the project directory:     
```bash
git clone <repository-url>
cd localcartesian
uv sync --dev
uv build
```

### Generate multiple wheels locally

For Linux
```bash
uvx cibuildwheel --platform linux --only "cp39-manylinux_x86_64 cp310-manylinux_x86_64 cp311-manylinux_x86_64 cp312-manylinux_x86_64"
```

For MacOS
```bash
uvx cibuildwheel --platform macos \
  --only "cp39-macosx_x86_64 cp310-macosx_x86_64 cp311-macosx_x86_64 cp312-macosx_x86_64 \
          cp39-macosx_arm64  cp310-macosx_arm64  cp311-macosx_arm64  cp312-macosx_arm64"
```


### Running Tests

```bash
uv sync --extra test
uv run pytest
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.