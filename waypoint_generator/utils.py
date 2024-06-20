import math
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")


def get_bounding_box(polygon):
    try:
        min_lat = min(point["latitude"] for point in polygon)
        max_lat = max(point["latitude"] for point in polygon)
        min_lon = min(point["longitude"] for point in polygon)
        max_lon = max(point["longitude"] for point in polygon)

        # Create the rectangle corners (assuming the rectangle is axis-aligned)
        bounding_box = [
            {"latitude": min_lat, "longitude": max_lon},
            {"latitude": max_lat, "longitude": max_lon},
            {"latitude": max_lat, "longitude": min_lon},
            {"latitude": min_lat, "longitude": min_lon},
            {"latitude": min_lat, "longitude": max_lon},
        ]
        logger_info.info(f'Bounding box generated {bounding_box}')

        return bounding_box
    except Exception as e:
        logger_error(f'Bounding box generating error {str(e)}')
        return []


def dms_to_decimal(degrees, minutes, seconds):
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def horizontal_move_point(lat, lon, distance, bearing):
    R = 6371e3  # Earth radius in meters
    bearing = math.radians(bearing)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance / R) + math.cos(lat1) * math.sin(distance / R) * math.cos(bearing))
    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
                             math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))

    return math.degrees(lat2), math.degrees(lon2)


def generate_horizontal_waypoints(polygon, altitude, overlapping_percentage, coverage_horizontal):
    # Constants
    # FOV = 100.0  # Field of View in meters
    FOV = coverage_horizontal
    overlap_distance = FOV * (overlapping_percentage / FOV)
    move_distance = FOV - overlap_distance
    start_move = -(move_distance - abs((FOV/2) - overlap_distance))
    # start_move = abs((FOV/2) - overlap_distance)

    # Find the bounding box
    min_lat = min(point["latitude"] for point in polygon)
    max_lat = max(point["latitude"] for point in polygon)
    min_lon = min(point["longitude"] for point in polygon)
    max_lon = max(point["longitude"] for point in polygon)

    # Find the start point (right-bottom corner)
    right_bottom = {"latitude": min_lat, "longitude": max_lon}
    start_lat, start_lon = horizontal_move_point(right_bottom["latitude"], right_bottom["longitude"], start_move, 0)
    start_lat, start_lon = horizontal_move_point(start_lat, start_lon, start_move, 270)

    # Generate waypoints
    waypoints = []
    lat, lon = start_lat, start_lon

    min_lat, min_lon = vertical_move_point(min_lat, min_lon, move_distance, 270)
    # while lat < max_lat:
    while lon > min_lon:
        waypoints.append({"latitude": lat, "longitude": lon})
        lat, lon = horizontal_move_point(lat, lon, move_distance, 270)  # Move left (west)
    return waypoints


def vertical_move_point(lat, lon, distance, bearing):
    R = 6371e3  # Earth radius in meters
    bearing = math.radians(bearing)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance / R) + math.cos(lat1) * math.sin(distance / R) * math.cos(bearing))
    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
                             math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))

    return math.degrees(lat2), math.degrees(lon2)


def generate_vertical_waypoints(polygon, altitude, overlapping_percentage, coverage_vertical):
    # Constants
    # FOV = 100.0  # Field of View in meters
    FOV = coverage_vertical
    overlap_distance = FOV * (overlapping_percentage / FOV)
    move_distance = FOV - overlap_distance
    start_move = -(move_distance - abs((FOV / 2) - overlap_distance))
    # start_move = abs((FOV / 2) - overlap_distance)

    # Find the bounding box
    min_lat = min(point["latitude"] for point in polygon)
    max_lat = max(point["latitude"] for point in polygon)
    min_lon = min(point["longitude"] for point in polygon)
    max_lon = max(point["longitude"] for point in polygon)

    # Find the start point (right-bottom corner)
    right_bottom = {"latitude": min_lat, "longitude": max_lon}
    begin_lat, begin_lon = vertical_move_point(right_bottom["latitude"], right_bottom["longitude"], start_move, 0)
    begin_lat, begin_lon = vertical_move_point(begin_lat, begin_lon, start_move, 270)

    # Generate waypoints
    waypoints = []
    lat, lon = begin_lat, begin_lon
    direction = 0  # 0 for upward, 180 for downward
    max_lat, max_lon = vertical_move_point(max_lat, max_lon, move_distance, direction)

    while lat <= max_lat:
        waypoints.append({"latitude": lat, "longitude": lon})
        lat, lon = vertical_move_point(lat, lon, move_distance, direction)

    return waypoints


def decimal_to_dms(decimal_degrees):
    is_positive = decimal_degrees >= 0
    decimal_degrees = abs(decimal_degrees)

    degrees = int(decimal_degrees)
    minutes_float = (decimal_degrees - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60

    if not is_positive:
        degrees = -degrees

    return degrees, minutes, seconds


def generate_all_points(vertical_points, horizontal_points): 
    # Extract latitudes and longitudes
    vertical_latitudes = [point['latitude'] for point in vertical_points]
    horizontal_longitudes = [point['longitude'] for point in horizontal_points]

    reverse = False
    all_points = []
    
    fast_lat = vertical_latitudes[0]
    last_lat = vertical_latitudes[-1]

    for lon in horizontal_longitudes:
        if not reverse:
            for lat in vertical_latitudes:
                all_points.append({'latitude': lat, 'longitude': lon})
                if last_lat == lat:
                    reverse = True
        else:
            for lat in vertical_latitudes[::-1]:
                all_points.append({'latitude': lat, 'longitude': lon})
                if last_lat == lat:
                    reverse = False

    return all_points


def plot_waypoints(bounding_box, polygon, all_points):
    fig, ax = plt.subplots()

    # Extracting latitude and longitude from primary points
    all_points_latitudes = [point['latitude'] for point in all_points]
    all_points_longitudes = [point['longitude'] for point in all_points]

    # Plotting secondary points with a different color
    ax.plot(all_points_longitudes, all_points_latitudes, 'bo-', marker='s', label='all Points')

    # Extracting latitude and longitude from bounding box points
    bounding_box_latitudes = [point['latitude'] for point in bounding_box]
    bounding_box_longitudes = [point['longitude'] for point in bounding_box]

    # Plotting bounding box points with a different color
    ax.plot(bounding_box_longitudes, bounding_box_latitudes, 'ro-', marker='x', label='Bounding box points')

    # Extracting latitude and longitude from user polygon points
    if polygon[0] != polygon[-1]:
        polygon.append(polygon[0])
    polygon_latitudes = [point['latitude'] for point in polygon]
    polygon_longitudes = [point['longitude'] for point in polygon]

    # Plotting user polygon points with a different color
    ax.plot(polygon_longitudes, polygon_latitudes, 'gs-', marker='o', label='User polygon points')

    # Adding labels and title
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Latitude and Longitude Points')
    ax.legend()

    # Show grid
    ax.grid(True)

    # Display the plot
    plt.show()


# Function to calculate FOV
def calculate_fov(sensor_size, focal_length):
    return 2 * math.degrees(math.atan(sensor_size / (2 * focal_length)))


# Function to calculate coverage area
def calculate_coverage(fov, height):
    return 2 * (height * math.tan(math.radians(fov / 2)))


def get_fov(height):
    # GoPro HERO9 Black specifications
    sensor_width = 6.17  # in mm
    sensor_height = 4.55  # in mm
    focal_length = 3  # in mm

    # Calculate horizontal and vertical FOV
    fov_horizontal = calculate_fov(sensor_width, focal_length)
    fov_vertical = calculate_fov(sensor_height, focal_length)

    # Calculate horizontal and vertical coverage
    coverage_horizontal = calculate_coverage(fov_horizontal, height)
    coverage_vertical = calculate_coverage(fov_vertical, height)

    return coverage_vertical, coverage_horizontal
