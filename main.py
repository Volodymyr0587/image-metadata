from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def extract_basic_metadata(image):
    """Extract basic metadata from an image."""
    return {
        "Filename": image.filename,
        "Image Size": image.size,
        "Image Height": image.height,
        "Image Width": image.width,
        "Image Format": image.format,
        "Image Mode": image.mode,
        "Image is Animated": getattr(image, "is_animated", False),
        "Frames in Image": getattr(image, "n_frames", 1),
    }


def extract_exif_data(image):
    """Extract EXIF data from an image."""
    exif_data = image._getexif()
    if not exif_data:
        print("No EXIF data found.")
        return {}

    exif = {}
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        if isinstance(value, bytes):
            try:
                value = value.decode()
            except UnicodeDecodeError:
                value = value.hex()
        exif[tag] = value
    return exif


def convert_to_degrees(value):
    """Convert GPS coordinates from EXIF format to degrees."""
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)


def extract_gps_coordinates(exif):
    """Extract and convert GPS coordinates to a human-readable format."""
    gps_info = exif.get("GPSInfo")
    if not gps_info:
        return None

    gps_data = {GPSTAGS.get(tag, tag): gps_info[tag] for tag in gps_info}
    try:
        lat = convert_to_degrees(gps_data["GPSLatitude"])
        lon = convert_to_degrees(gps_data["GPSLongitude"])
        lat_ref = gps_data["GPSLatitudeRef"]
        lon_ref = gps_data["GPSLongitudeRef"]

        if lat_ref != "N":
            lat = -lat
        if lon_ref != "E":
            lon = -lon

        google_maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        return {
            "Latitude": f"{lat}° {lat_ref}",
            "Longitude": f"{lon}° {lon_ref}",
            "Google Maps Link": google_maps_link,
        }
    except KeyError:
        return None


def display_metadata(metadata, title):
    """Display metadata in a formatted way."""
    print(f"\n{title}")
    print("=" * len(title))
    for key, value in metadata.items():
        print(f"{key:25}: {value}")


def main(image_path):
    try:
        # Open the image
        image = Image.open(image_path)

        # Extract basic metadata
        basic_metadata = extract_basic_metadata(image)
        display_metadata(basic_metadata, "Basic Metadata")

        # Extract EXIF data
        exif_metadata = extract_exif_data(image)
        display_metadata(exif_metadata, "EXIF Metadata")

        # Extract and display GPS coordinates
        gps_coordinates = extract_gps_coordinates(exif_metadata)
        if gps_coordinates:
            display_metadata(gps_coordinates, "GPS Coordinates")
        else:
            print("\nNo GPS information found.")
    except FileNotFoundError:
        print(f"Error: File '{image_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    image_file = "20241227_163205.jpg"  # Replace with your image file
    main(image_file)
