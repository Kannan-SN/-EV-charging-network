
import math
from typing import Tuple, List, Dict, Any
from geopy.distance import geodesic


def calculate_distance(
    coord1: Tuple[float, float], coord2: Tuple[float, float]
) -> float:
    """Calculate distance between two coordinates in kilometers"""
    return geodesic(coord1, coord2).kilometers


def get_bounding_box(lat: float, lon: float, radius_km: float) -> Dict[str, float]:
    """Get bounding box coordinates for a given center point and radius"""
    # Rough approximation: 1 degree lat ≈ 111 km, 1 degree lon ≈ 111 km * cos(lat)
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * math.cos(math.radians(lat)))

    return {
        "north": lat + lat_offset,
        "south": lat - lat_offset,
        "east": lon + lon_offset,
        "west": lon - lon_offset,
    }


def is_within_radius(
    center: Tuple[float, float], point: Tuple[float, float], radius_km: float
) -> bool:
    """Check if a point is within radius of center"""
    return calculate_distance(center, point) <= radius_km


def find_optimal_grid_points(
    center_lat: float, center_lon: float, radius_km: float, grid_size: int = 5
) -> List[Tuple[float, float]]:
    """Generate grid points for systematic location analysis"""
    points = []
    step = radius_km / grid_size

    for i in range(-grid_size, grid_size + 1):
        for j in range(-grid_size, grid_size + 1):
            lat_offset = i * step / 111.0
            lon_offset = j * step / (111.0 * math.cos(math.radians(center_lat)))

            new_lat = center_lat + lat_offset
            new_lon = center_lon + lon_offset

            # Check if point is within radius
            if (
                calculate_distance((center_lat, center_lon), (new_lat, new_lon))
                <= radius_km
            ):
                points.append((new_lat, new_lon))

    return points
