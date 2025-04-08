import datetime
import pytz
import numpy as np
from timezonefinder import TimezoneFinder
from typing import Union, Tuple, List, Dict, Optional, Any
import requests
import json
import functools
import concurrent.futures
from astral import LocationInfo
from astral.sun import sun

# Cache for timezone lookups to avoid redundant calculations
TIMEZONE_CACHE: Dict[Tuple[float, float], str] = {}

# Initialize TimezoneFinder once for better performance
tf = TimezoneFinder()


@functools.lru_cache(maxsize=1024)
def get_timezone_str(lat: float, lon: float) -> Optional[str]:
    """Get timezone string with caching for performance."""
    # Round coordinates to reduce cache misses while maintaining accuracy
    # 4 decimal places is approximately 11 meters of precision
    cache_key = (round(lat, 4), round(lon, 4))

    if cache_key in TIMEZONE_CACHE:
        return TIMEZONE_CACHE[cache_key]

    timezone_str = tf.timezone_at(lat=lat, lng=lon)
    TIMEZONE_CACHE[cache_key] = timezone_str
    return timezone_str


def get_local_time(
        coordinates: Union[Tuple[float, float], List[Tuple[float, float]]],
        timestamp: datetime.datetime = None
) -> Union[datetime.datetime, List[datetime.datetime]]:
    """
    Convert geographic coordinates to local time.

    Args:
        coordinates: Either a single (latitude, longitude) tuple or a list of such tuples.
                    Latitude and longitude should be in degrees.
        timestamp: Optional datetime object (UTC). If None, current UTC time is used.

    Returns:
        Either a single datetime object or a list of datetime objects with local time.
    """
    # Use current time if no timestamp provided
    if timestamp is None:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
    elif timestamp.tzinfo is None:
        # Ensure timestamp is timezone-aware (UTC)
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)

    # Handle single coordinate pair
    if isinstance(coordinates, (tuple, list)) and len(coordinates) == 2 and isinstance(coordinates[0], (int, float)):
        lat, lon = coordinates
        return _single_coordinate_to_local_time(lat, lon, timestamp)

    # Handle batch processing of multiple coordinate pairs
    return _batch_coordinates_to_local_time(coordinates, timestamp)


def _single_coordinate_to_local_time(lat: float, lon: float, timestamp: datetime.datetime) -> datetime.datetime:
    """Process a single coordinate pair to get local time."""
    timezone_str = get_timezone_str(lat, lon)

    if timezone_str is None:
        # Fall back to approximate timezone based on longitude
        utc_offset = round(lon / 15)
        return timestamp + datetime.timedelta(hours=utc_offset)

    # Get the timezone object
    timezone = pytz.timezone(timezone_str)

    # Convert UTC time to local time
    return timestamp.astimezone(timezone)


def _process_coordinate_batch(coords_batch: List[Tuple[float, float]], timestamp: datetime.datetime) -> List[
    datetime.datetime]:
    """Process a batch of coordinates to local times. Used for parallel processing."""
    results = []
    for lat, lon in coords_batch:
        results.append(_single_coordinate_to_local_time(lat, lon, timestamp))
    return results


def _batch_coordinates_to_local_time(
        coordinates: List[Tuple[float, float]],
        timestamp: datetime.datetime
) -> List[datetime.datetime]:
    """Process multiple coordinate pairs efficiently using parallel processing."""
    # Determine optimal number of workers and batch size based on input size
    num_coords = len(coordinates)

    if num_coords <= 100:
        # For small datasets, process serially to avoid overhead
        return [_single_coordinate_to_local_time(lat, lon, timestamp) for lat, lon in coordinates]

    # For larger datasets, use parallel processing
    num_workers = min(32, max(4, num_coords // 250))  # Adjust based on system capabilities
    batch_size = max(1, num_coords // num_workers)

    # Split coordinates into batches
    batches = [coordinates[i:i + batch_size] for i in range(0, num_coords, batch_size)]

    # Process batches in parallel
    all_results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_batch = {
            executor.submit(_process_coordinate_batch, batch, timestamp): batch
            for batch in batches
        }

        for future in concurrent.futures.as_completed(future_to_batch):
            batch_results = future.result()
            all_results.extend(batch_results)

    return all_results


def get_user_coordinates() -> Tuple[float, float]:
    """
    Get the user's current geographic coordinates using IP geolocation.

    Returns:
        A tuple containing (latitude, longitude)
    """
    try:
        # Using the free IP Geolocation API
        response = requests.get('https://ipapi.co/json/', timeout=3)
        data = response.json()

        if 'latitude' in data and 'longitude' in data:
            return (data['latitude'], data['longitude'])

        # Fallback to another service if the first one fails
        response = requests.get('https://ipinfo.io/json', timeout=3)
        data = response.json()

        if 'loc' in data:
            lat, lon = map(float, data['loc'].split(','))
            return (lat, lon)

        print("Could not determine coordinates from IP geolocation services.")
        return get_user_input_coordinates()

    except Exception as e:
        print(f"Error getting location from IP: {e}")
        return get_user_input_coordinates()


def get_user_input_coordinates() -> Tuple[float, float]:
    """
    Ask the user to manually input their coordinates.

    Returns:
        A tuple containing (latitude, longitude)
    """
    print("Please enter your coordinates manually:")

    while True:
        try:
            lat = float(input("Enter latitude (-90 to 90): "))
            if not -90 <= lat <= 90:
                print("Latitude must be between -90 and 90 degrees.")
                continue

            lon = float(input("Enter longitude (-180 to 180): "))
            if not -180 <= lon <= 180:
                print("Longitude must be between -180 and 180 degrees.")
                continue

            return (lat, lon)

        except ValueError:
            print("Please enter valid numbers for coordinates.")


def get_sun_information(lat: float, lon: float, date: datetime.date = None) -> Dict[str, Any]:
    """
    Calculate sunrise, sunset, and other sun information for given coordinates and date.

    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        date: Optional date to calculate for. If None, current date is used.

    Returns:
        Dictionary containing sunrise, sunset, dawn, dusk, noon, and day length information
    """
    # Use current date if none provided
    if date is None:
        date = datetime.datetime.now(datetime.timezone.utc).date()

    # Get timezone for the coordinates
    timezone_str = get_timezone_str(lat, lon)
    if timezone_str is None:
        # Fallback for coordinates without timezone data
        # Using UTC with longitude offset as approximation
        timezone = datetime.timezone(datetime.timedelta(hours=round(lon / 15)))
        timezone_name = f"UTC{'+' if lon >= 0 else ''}{round(lon / 15)}"
    else:
        timezone = pytz.timezone(timezone_str)
        timezone_name = timezone_str

    # Create location object for astral calculations
    location = LocationInfo(
        name="CustomLocation",
        region="World",
        timezone=timezone_name,
        latitude=lat,
        longitude=lon
    )

    # Calculate sun information
    s = sun(location.observer, date=date, tzinfo=timezone)

    # Calculate day length
    day_length = s['sunset'] - s['sunrise']
    hours, remainder = divmod(day_length.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    return {
        'sunrise': s['sunrise'],
        'sunset': s['sunset'],
        'dawn': s['dawn'],
        'dusk': s['dusk'],
        'noon': s['noon'],
        'day_length': f"{int(hours)}h {int(minutes)}m",
        'day_length_seconds': day_length.total_seconds(),
        'timezone': timezone_name
    }


def format_time(dt: datetime.datetime) -> str:
    """Format datetime object to a readable string."""
    return dt.strftime('%A, %B %d, %Y %I:%M:%S %p %Z')


def format_time_short(dt: datetime.datetime) -> str:
    """Format datetime object to a short readable string."""
    return dt.strftime('%I:%M:%S %p')


# Example usage
if __name__ == "__main__":
    print("Geographic Coordinates to Local Time Converter")
    print("---------------------------------------------")

    # Get user's coordinates
    user_coords = get_user_coordinates()
    lat, lon = user_coords

    print(f"\nYour detected coordinates: {lat:.4f}°, {lon:.4f}°")

    # Get timezone and current time
    user_local_time = get_local_time(user_coords)
    print(f"Your current local time: {format_time(user_local_time)}")

    # Get sunrise and sunset information
    try:
        print("\nSun Information for your location:")

        # For today
        today = user_local_time.date()
        sun_info_today = get_sun_information(lat, lon, today)

        print(f"Today ({today}):")
        print(f"  Sunrise: {format_time_short(sun_info_today['sunrise'])}")
        print(f"  Sunset:  {format_time_short(sun_info_today['sunset'])}")
        print(f"  Day length: {sun_info_today['day_length']}")

        # For tomorrow
        tomorrow = today + datetime.timedelta(days=1)
        sun_info_tomorrow = get_sun_information(lat, lon, tomorrow)

        print(f"\nTomorrow ({tomorrow}):")
        print(f"  Sunrise: {format_time_short(sun_info_tomorrow['sunrise'])}")
        print(f"  Sunset:  {format_time_short(sun_info_tomorrow['sunset'])}")
        print(f"  Day length: {sun_info_tomorrow['day_length']}")

        # Calculate day length change
        day_length_change = sun_info_tomorrow['day_length_seconds'] - sun_info_today['day_length_seconds']
        change_minutes, change_seconds = divmod(abs(day_length_change), 60)
        change_sign = "+" if day_length_change > 0 else "-"
        print(f"  Day length change: {change_sign}{int(change_minutes)}m {int(change_seconds)}s")

    except Exception as e:
        print(f"Error calculating sun information: {e}")

    # Example of additional locations
    print("\nCurrent local times around the world:")
    locations = [
        (40.7128, -74.0060),  # New York
        (51.5074, -0.1278),  # London
        (35.6762, 139.6503),  # Tokyo
        (19.0760, 72.8777),  # Mumbai
    ]

    # Get local times for all locations using optimized batch function
    local_times = get_local_time(locations)

    # Print results
    cities = ["New York", "London", "Tokyo", "Mumbai"]
    for city, local_time in zip(cities, local_times):
        print(f"{city}: {format_time_short(local_time)}")

    print("\nProgram completed successfully.")