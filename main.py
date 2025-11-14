import ttkbootstrap as ttk
from tkinter import Tk
import os

# Importer tes fichiers de fenêtres
from fenetre1_selection import FenetreSelection
from fenetre2_metadata import FenetreMetadata
from fenetre3_map import FenetreMap

class MainApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Application de Géolocalisation")
        self.geometry("1000x700")
         

       
        self.f1 = FenetreSelection(self, self.go_to_metadata)
        self.f2 = FenetreMetadata(self,self.go_to_selection, self.go_to_map)
        self.f3 = FenetreMap(self, self.back_to_metadata)

       
        self.f1.pack(fill="both", expand=True)
      

    # Fenetre1 à Fenetre2
    def go_to_metadata(self, photos):
        
        if not photos:
            ttk.messagebox.showwarning("Avertissement", "Veuillez sélectionner au moins une photo !")
            return

        
        self.f2.afficher_photos(photos)
        self.f1.pack_forget()
        self.f2.pack(fill="both", expand=True)


        # Fenetre2 à Fenetre3
    def go_to_map(self):
        self.f3.coords_list = [
            {"latitude": p["latitude"], "longitude": p["longitude"], "name": os.path.basename(p["photo_path"])}
            for p in self.f2.photos_data
            if isinstance(p["latitude"], float) and isinstance(p["longitude"], float)
        ]

        if not self.f3.coords_list:
            ttk.messagebox.showwarning("Avertissement", "y a pas de coordonnées GPS valides !")
            return

        self.f2.pack_forget()
        self.f3.pack(fill="both", expand=True)
        self.f3.afficher_carte()
    


    def go_to_selection(self):
        self.f2.pack_forget()
        self.f1.pack(fill="both", expand=True)

    
    def back_to_metadata(self):
        self.f3.pack_forget()
        self.f2.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
