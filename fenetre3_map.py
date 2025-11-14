import ttkbootstrap as ttk
from tkinter import messagebox
import backend
import os
import webbrowser

class FenetreMap(ttk.Frame):
    def __init__(self, master, go_back_callback):
        super().__init__(master)
        self.go_back_callback = go_back_callback
        self.coords_list = []  
        self.transport_mode = ttk.StringVar(value="walking")

   

        #le titre
        title = ttk.Label(self, text="Carte de Géolocalisation", font=("Segoe UI", 28, "bold"))
        title.pack(pady=(20, 20))

        # label de mode de transport
        self.labelTransMod = ttk.Label(self,
                                        text=self.txtLabelTraspo(),
                                        font=("Segoe UI", 12, "bold")
                                        )
        self.labelTransMod.pack(padx=5,pady=20)
        # des radiobutton pour choisir le mode de transport
        radio_walk= ttk.Radiobutton(self,
                                    text="🚶 À pied",
                                    variable=self.transport_mode,
                                    value="walking",
                                    command=self.transChanger
                                    )
        radio_velo = ttk.Radiobutton(self,
                                    text="🚴 Vélo", 
                                    variable=self.transport_mode,
                                    value="cycling", 
                                    command=self.transChanger
                                    )
        radio_voit = ttk.Radiobutton(self,
                                    text="🚗 Voiture", 
                                    variable=self.transport_mode,
                                    value="driving",
                                    command=self.transChanger
                                    )
        radio_walk.pack(side="left", padx=10)
        radio_velo.pack(side="left", padx=10)
        radio_voit.pack(side="left", padx=10)



        self.btn_route = ttk.Button(self,
                                    text="🚶 Afficher l'itinéraire", 
                                    bootstyle="success",
                                   command=self.itineraireCart)
        self.btn_route.pack(side="left", padx=10)

        btn_info = ttk.Button(self, 
                              text="ℹ️ Détails itinéraire", 
                              bootstyle="info", 
                              command=self.show_route)
        btn_info.pack(side="left", padx=10)

        btn_export = ttk.Button(self, 
                                text="💾 Exporter la carte", 
                                bootstyle="secondary",
                                command=self.carteSeul)
        btn_export.pack(side="left", padx=10)

        btn_back = ttk.Button(self, 
                              text="⬅️ Retour", 
                              bootstyle="secondary", 
                              command=self.go_back_callback)
        btn_back.pack(side="right", padx=10)



   
     # retourner le nouveau text de label apres chaque choix de mode trasport 
    def txtLabelTraspo(self):
        labels = {"walking": "✅ Mode actuel : 🚶 À pied",
                  "cycling": "✅ Mode actuel : 🚴 Vélo",
                  "driving": "✅ Mode actuel : 🚗 Voiture"}
        return labels.get(self.transport_mode.get())

    #faire la mise a jour de label text si il a cliquer sur un autre mode de transport
    def transChanger(self):
        self.labelTransMod.config(text=self.txtLabelTraspo())


    # affecher  la carte avec l'itineraire de transport choisis   
    def itineraireCart(self):
        self.generate_backend_map(with_route=True, open_after=True)
        
    # afficher les lieu dans la carte sans l'itineraire
    def carteSeul(self):
       
        if not self.coords_list:
            messagebox.showwarning("Attention", "Aucune coordonnée GPS valide pour exporter la carte.")
            return
        
        self.generate_backend_map(open_after=True, with_route=False)

    #elle va appeler la fonction cree_map de backend , afficher l'itineraire si  with_route=true,et ouvrire la carte si  open_after=true
    def generate_backend_map(self, with_route=True, open_after=False):
       
        if not self.coords_list:
            messagebox.showwarning("Attention", "Aucune coordonnée GPS valide pour générer la carte.")
            return

        locs = [(c["latitude"], c["longitude"]) for c in self.coords_list]
        
        m = backend.cree_map(locs)
        


        if with_route:
            mode = self.transport_mode.get()
            if mode == "walking":
                backend.chemin_pieds(locs, m)
            elif mode == "cycling":
                backend.chemin_velo(locs, m)
            elif mode == "driving":
                backend.chemin_voiture(locs, m)

        

        if open_after:
            backend.ouvrir_map(m)


    # calcule distance totale
    def calculate_perimeter(self):
        if len(self.coords_list) < 2:
            return 0.0
        total_distance = 0.0
        for i in range(len(self.coords_list)):
            c1 = self.coords_list[i]
            c2 = self.coords_list[(i + 1) % len(self.coords_list)]
            lat_diff = abs(c1["latitude"] - c2["latitude"])
            lon_diff = abs(c1["longitude"] - c2["longitude"])
            # le théorème de Pythagore pour obtenir une distance
            distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
            total_distance += distance
        return total_distance

    def show_route(self):
        if not self.coords_list:
            messagebox.showinfo("Détails de l'itinéraire", "Aucune donnée GPS disponible.")
            return
        route_info = " Détails de l'itinéraire:\n\n"
        for i, coord in enumerate(self.coords_list, 1):
            route_info += f"image {i}: {coord['name']}\n"
            route_info += f"  📌 latitude:{coord['latitude']:.2f}, longitude:{coord['longitude']:.2f}\n"
            if i < len(self.coords_list):
                route_info += "  ↓\n"
        route_info += f"\n📏 Distance totale: ~{self.calculate_perimeter():.2f} km"
        messagebox.showinfo("Détails de l'itinéraire", route_info)
