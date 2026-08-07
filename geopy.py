import sys
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Set up geolocator with a specific timeout and user agent
geolocator = Nominatim(user_agent="latvia_distance_console_calc", timeout=10)

print("=== Latvian Address Distance Calculator ===")
print("Please enter the addresses below.\n")

# Hardcoded addresses from your request for immediate testing
address_1 = "Piebalgas, LV-3933, Latvija"
address_2 = "Nijverheidsweg 19, 3641 RP Mijdrecht, Netherlands"

print(f"Address 1: {address_1}")
print(f"Address 2: {address_2}")
print("\nSearching coordinates...")

try:
    # Get coordinates for Address 1
    loc1 = geolocator.geocode(address_1)
    if not loc1:
        print("Error: Could not find Address 1. Try a simpler format.")
        sys.exit()
        
    # Get coordinates for Address 2
    loc2 = geolocator.geocode(address_2)
    if not loc2:
        print("Error: Could not find Address 2. Try a simpler format.")
        sys.exit()

    # Store coordinates as (latitude, longitude) tuples
    coords_1 = (loc1.latitude, loc1.longitude)
    coords_2 = (loc2.latitude, loc2.longitude)

    print(f"-> Found Address 1: {loc1.address} ({coords_1})")
    print(f"-> Found Address 2: {loc2.address} ({coords_2})")

    # Mathematically calculate the geodesic distance ("as the crow flies") in km
    distance_km = geodesic(coords_1, coords_2).kilometers

    print("\n" + "="*30)
    print(f"SUCCESS: Distance is {distance_km:.2f} km")
    print("="*30)

except Exception as e:
    print(f"\nAn error occurred during calculation: {e}")
