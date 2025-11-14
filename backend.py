
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


#Fonction pour retourner la carte cree, et ajouter les localisations:
def cree_map(localisations):
    #instialiser la partie qui va etre aficher lors de l'ouverture du map
    first_lat, first_lon = localisations[0]
    #premier zoom sur les localisations
    m = folium.Map(location=[first_lat, first_lon], zoom_start=6)
    #ajouter des markers pour chaque position
    for lat,long in localisations:
        folium.Marker([lat,long]).add_to(m)
    m.fit_bounds(localisations)
    return m

#ouvre la carte dans le navigateur
def ouvrir_map(m):
    m.save("map.html")
    webbrowser.open("map.html")

#Fonction dessiner le chemin si c'etais a pieds 
def chemin_pieds(localisations, m): #donner array des localisations, et la carte comme input
    client=openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjU5ZDY4NGY4YmFmYzRlOTlhZGZiZDQxMmFhNGFiZTU4IiwiaCI6Im11cm11cjY0In0=")
    coords_ors = [[lon, lat] for (lat, lon) in localisations]
    route=client.directions(coords_ors, profile='foot-walking', format='geojson')
    folium.GeoJson(route).add_to(m)


#Fonction dessiner le chemin si c'etais avec voiture 
def chemin_voiture(localisations, m):
    client=openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjU5ZDY4NGY4YmFmYzRlOTlhZGZiZDQxMmFhNGFiZTU4IiwiaCI6Im11cm11cjY0In0=")
    coords_ors = [[lon, lat] for (lat, lon) in localisations]
    route=client.directions(coords_ors, profile='driving-car', format='geojson')
    folium.GeoJson(route).add_to(m)


#Fonction dessiner le chemin si c'etais avec velo 
def chemin_velo(localisations, m): 
    client=openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjU5ZDY4NGY4YmFmYzRlOTlhZGZiZDQxMmFhNGFiZTU4IiwiaCI6Im11cm11cjY0In0=")
    coords_ors = [[lon, lat] for (lat, lon) in localisations]
    route=client.directions(coords_ors, profile='cycling-regular', format='geojson')
    folium.GeoJson(route).add_to(m)



