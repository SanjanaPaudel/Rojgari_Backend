import requests

NOMINATIM_REVERSE_URL =  "https://nominatim.openstreetmap.org/reverse"

def reverse_geocode(latitude, longitude):
    """
    Convert coordinates into a human-readable address string
    using OpenStreetMap's Nominatim reverse geocoding API

    Return the address string, or None if it could not be resolved
    """

    params = {
        "lat" : latitude,
        "lon" : longitude,
        "format" : "json",
    }

    headers = {
        "User-Agent" : "RojgariApp/1.0 (adhikari.dinesh781@gmail.com)",
    }

    try:
        response = requests.get(
            NOMINATIM_REVERSE_URL,
            params=params,
            headers=headers,
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("display_name")
    
    except requests.ReqeustException:
        return None