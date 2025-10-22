#!/usr/bin/env python3

import numpy as np
from localcartesian import gps2xy, xy2gps


def test_gps2xy_conversion():
    """Test GPS to local cartesian conversion with realistic values."""
    # Realistic GPS coordinates (lat, lon pairs)
    gps_coords = [
        [40.7128, -74.0060],  # New York City
        [40.7589, -73.9851],  # Times Square
        [40.6892, -74.0445],  # Statue of Liberty
    ]

    # Origin point (lat, lon, altitude)
    origin_latlonalt = [40.7128, -74.0060, 0.0]  # NYC as origin

    # Convert GPS to local cartesian coordinates
    local_coords = gps2xy(gps_coords, origin_latlonalt)
    local_coords_array = np.array(local_coords)

    # Assertions
    assert isinstance(local_coords, list)
    assert len(local_coords) == 3  # Should have 3 points
    assert local_coords_array.shape == (3, 2)  # 3 points, x,y coordinates

    # First point should be at origin (approximately)
    assert abs(local_coords[0][0]) < 1e-10  # x should be ~0
    assert abs(local_coords[0][1]) < 1e-10  # y should be ~0

    print("GPS coordinates:")
    for i, coord in enumerate(gps_coords):
        print(f"  Point {i + 1}: {coord}")
    print("\nLocal Cartesian coordinates:")
    for i, coord in enumerate(local_coords):
        print(f"  Point {i + 1}: [{coord[0]:.2f}, {coord[1]:.2f}] meters")


def test_xy2gps_conversion():
    """Test local cartesian to GPS conversion."""
    # Local coordinates in meters from origin
    local_coords = [
        [0.0, 0.0],  # Origin
        [1000.0, 0.0],  # 1km east
        [0.0, 1000.0],  # 1km north
    ]

    # Origin point (lat, lon, altitude)
    origin_latlonalt = [40.7128, -74.0060, 0.0]  # NYC as origin

    # Convert local coordinates to GPS
    gps_coords = xy2gps(local_coords, origin_latlonalt)
    gps_coords_array = np.array(gps_coords)

    # Assertions
    assert isinstance(gps_coords, list)
    assert len(gps_coords) == 3  # Should have 3 points
    assert gps_coords_array.shape == (3, 2)  # 3 points, lat,lon coordinates

    # First point should be at origin
    assert abs(gps_coords[0][0] - origin_latlonalt[0]) < 1e-10
    assert abs(gps_coords[0][1] - origin_latlonalt[1]) < 1e-10

    print("Local Cartesian coordinates:")
    for i, coord in enumerate(local_coords):
        print(f"  Point {i + 1}: {coord} meters")
    print("\nGPS coordinates:")
    for i, coord in enumerate(gps_coords):
        print(f"  Point {i + 1}: [{coord[0]:.8f}, {coord[1]:.8f}]")


def test_round_trip_conversion():
    """Test that GPS -> XY -> GPS gives back original coordinates."""
    # Original GPS coordinates
    original_gps = [
        [40.7128, -74.0060],  # New York City
        [40.7589, -73.9851],  # Times Square
    ]

    # Origin point
    origin_latlonalt = [40.7128, -74.0060, 0.0]

    # Convert GPS -> XY -> GPS
    local_coords = gps2xy(original_gps, origin_latlonalt)
    recovered_gps = xy2gps(local_coords, origin_latlonalt)

    # Check that we get back the original coordinates (within tolerance)
    for orig, recovered in zip(original_gps, recovered_gps):
        assert abs(orig[0] - recovered[0]) < 1e-6  # latitude (within 1 meter precision)
        assert (
            abs(orig[1] - recovered[1]) < 1e-6
        )  # longitude (within 1 meter precision)

    print("Round-trip conversion test passed!")


if __name__ == "__main__":
    test_gps2xy_conversion()
    test_xy2gps_conversion()
    test_round_trip_conversion()
