
#les bibliotheques utilisees:
from tkinter import*
from exif import Image
import os
import folium
import exif
import openrouteservice
import webbrowser

#fonction pour convertir les donnees en decimal
def todecimal(dms, ref):
    deg, min, sec = dms 
    decimal = deg + min/60 + sec/3600
    if ref.upper() in ['W', 'S']:
        decimal *= -1
    return decimal

#Fonction pour la verification des donnees exif:
def verifier(img):
    
    if(img.has_exif):
        return True
    return False

#Fonction pour verifier que les donnees gps existent:
def verifier_gps(img):

    if(hasattr(img, "gps_latitude")):
        if(hasattr(img, "gps_longitude")):
            if(hasattr(img, "gps_latitude_ref")):
                if(hasattr(img, "gps_longitude_ref")):
                    return True
    return False


#Fonction pour cree la carte, et ajouter les localisations:
def cree_map(localisations):
    #instialiser la partie qui va etre aficher lors de l'ouverture du map
    first_lat, first_lon = localisations[0]
    #premier zoom sur les localisations
    m = folium.Map(location=[first_lat, first_lon], zoom_start=6)
    #ajouter des markers pour chaque position
    for lat,long in localisations:
        folium.Marker([lat,long]).add_to(m)
    m.fit_bounds(localisations)
    m.save("map.html")
    webbrowser.open("map.html") #ouvrir la carte automatiquement


#Fonction dessiner le chemin si c'etais a pieds 
def chemin_pieds(localisations, m): #donner array des localisations, et la carte comme input
    client=openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjU5ZDY4NGY4YmFmYzRlOTlhZGZiZDQxMmFhNGFiZTU4IiwiaCI6Im11cm11cjY0In0=")
    for i in localisations:
        route=client.directions(localisations, profile='foot_walking', format='geojson')
        folium.GeoJson(route).add_to(m)


#Fonction dessiner le chemin si c'etais avec voiture 
def chemin_voiture(localisations, m):
    client=openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjU5ZDY4NGY4YmFmYzRlOTlhZGZiZDQxMmFhNGFiZTU4IiwiaCI6Im11cm11cjY0In0=")
    for i in localisations:
        route=client.directions(localisations, profile='driving_car', format='geojson')
        folium.GeoJson(route).add_to(m)


#Fonction dessiner le chemin si c'etais avec velo 
def chemin_velo(localisations, m): 
    client=openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjU5ZDY4NGY4YmFmYzRlOTlhZGZiZDQxMmFhNGFiZTU4IiwiaCI6Im11cm11cjY0In0=")
    route=client.directions([(lon, lat) for (lat, lon) in localisations], profile='cycling_road', format='geojson')
    folium.GeoJson(route).add_to(m)


#La fonction main:

#On sauvgarde les photos dans un dossier, et tanq que le dossier n'est pas vide on repete la meme chose
image_folder = "images"
#Stocker les localisation dans un array du tuples
localisation =[]
for filename in os.listdir(image_folder):
    #verifier que les photo ont une extension jpg ou jpeg
    if filename.lower().endswith((".jpg", ".jpeg")):
        filepath = os.path.join(image_folder, filename)
        with open(filepath, "rb") as f:
            img=Image(f)
            if(verifier(img)):
                if(verifier_gps(img)):
                    lat = todecimal(img.gps_latitude, img.gps_latitude_ref)
                    lon = todecimal(img.gps_longitude, img.gps_longitude_ref)
                    localisation.append((lat,lon))

cree_map(localisation)

