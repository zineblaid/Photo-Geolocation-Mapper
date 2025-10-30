
import os
from exif import Image
import folium
import webbrowser


def dms_to_decimal(dms, ref):
    deg, min, sec = dms
    decimal = deg + min/60 + sec/3600
    if ref.upper() in ['W', 'S']:
        decimal *= -1
    return decimal


image_folder = "images"
locations = []

for filename in os.listdir(image_folder):
    if filename.endswith(".jpg") or filename.endswith(".jpeg"):
        filepath = os.path.join(image_folder, filename)
        with open(filepath, "rb") as f:
            img = Image(f)
            if img.has_exif and img.has("gps_latitude") and img.has("gps_longitude"):
                lat = dms_to_decimal(img.gps_latitude, img.gps_latitude_ref)
                lon = dms_to_decimal(img.gps_longitude, img.gps_longitude_ref)
                locations.append((lat, lon, filename))


if locations:
    first_lat, first_lon, _ = locations[0]
    map = folium.Map(location=[first_lat, first_lon], zoom_start=15)
    for lat, lon, filename in locations:
        folium.Marker([lat, lon], popup=filename).add_to(map)
    map.save("map.html")


print("Carte générée !")
choice = input("Tape 1 pour ouvrir la carte : ")
if choice == "1":
    webbrowser.open("map.html")


