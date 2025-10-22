#!/usr/bin/env python3
"""
Example usage of the localcartesian package.
"""

import numpy as np
from localcartesian import gps2xy, xy2gps


def main():
    print("LocalCartesian Example")
    print("=" * 50)

    # Define some GPS coordinates around New York City
    gps_coords = [
        [40.7128, -74.0060],  # New York City (origin)
        [40.7589, -73.9851],  # Times Square
        [40.6892, -74.0445],  # Statue of Liberty
        [40.7831, -73.9712],  # Central Park
    ]

    # Use NYC as the origin point (lat, lon, altitude)
    origin = [40.7128, -74.0060, 0.0]

    print("GPS Coordinates:")
    for i, coord in enumerate(gps_coords):
        print(f"  Point {i + 1}: [{coord[0]:.6f}, {coord[1]:.6f}]")

    print(f"\nOrigin: [{origin[0]:.6f}, {origin[1]:.6f}, {origin[2]:.1f}]")

    # Convert GPS to local Cartesian coordinates
    print("\nConverting GPS to local Cartesian coordinates...")
    local_coords = gps2xy(gps_coords, origin)

    print("Local Cartesian Coordinates (meters):")
    for i, coord in enumerate(local_coords):
        print(f"  Point {i + 1}: [{coord[0]:.2f}, {coord[1]:.2f}]")

    # Convert back to GPS coordinates to verify
    print("\nConverting back to GPS coordinates...")
    gps_recovered = xy2gps(local_coords, origin)

    print("Recovered GPS Coordinates:")
    for i, coord in enumerate(gps_recovered):
        print(f"  Point {i + 1}: [{coord[0]:.6f}, {coord[1]:.6f}]")

    # Check accuracy
    print("\nAccuracy Check:")
    for i, (orig, recovered) in enumerate(zip(gps_coords, gps_recovered)):
        lat_diff = abs(orig[0] - recovered[0])
        lon_diff = abs(orig[1] - recovered[1])
        print(f"  Point {i + 1}: lat_diff={lat_diff:.2e}, lon_diff={lon_diff:.2e}")


if __name__ == "__main__":
    main()
