import ttkbootstrap as ttk
from PIL import Image, ImageTk
import os
from exif import Image as ExifImage
import backend 

class FenetreMetadata(ttk.Frame):
    def __init__(self, master,switch_to_selection, switch_to_map):
        super().__init__(master)
        self.switch_to_selection = switch_to_selection 
        self.switch_to_map = switch_to_map 
        self.photos_data = []
        

    def afficher_photos(self, photos):
    # Supprimer tout contenu précédent
        for widget in self.winfo_children():
            widget.destroy()
        style = ttk.Style()
        style.configure("Black.TFrame", background="black")
        main_container = ttk.Frame(self, style="Black.TFrame", padding=30)
        main_container.pack(fill="both", expand=True)

        # Header
        header_frame = ttk.Frame(main_container,style="Black.TFrame")
        header_frame.pack(pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="📋 Métadonnées GPS",
            font=("Segoe UI", 32, "bold"),
            bootstyle="light",
            background="black"
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            header_frame,
            text="Informations de géolocalisation extraites des photos",
            font=("Segoe UI", 12),
            bootstyle="secondary",
            background="black"
        )
        subtitle_label.pack(pady=(5, 0))

        # Canvas scrollable
        canvas_frame = ttk.Frame(main_container)
        canvas_frame.pack(fill="both", expand=True, pady=(0, 20))

        canvas = ttk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Récupérer les métadonnées réelles des photos
        self.photos_data = []
        for photo_path in photos:
            try:
                with open(photo_path, "rb") as f:
                    img = ExifImage(f)

            # Vérifier EXIF + GPS
                if img.has_exif and backend.verifier_gps(img):
                    lat = backend.todecimal(img.gps_latitude, img.gps_latitude_ref)
                    lon = backend.todecimal(img.gps_longitude, img.gps_longitude_ref)
                    date = img.datetime_original if hasattr(img, "datetime_original") else "Non disponible"
                    altitude = img.gps_altitude if hasattr(img, "gps_altitude") else "Non disponible"

                    self.photos_data.append({
                        "photo_path": photo_path,
                        "latitude": lat,
                        "longitude": lon,
                        "altitude": altitude,
                        "date": date
                    })
                else:
                    self.photos_data.append({
                        "photo_path": photo_path,
                        "latitude": "N/A",
                        "longitude": "N/A",
                        "altitude": "N/A",
                        "date": "N/A"
                    })

            except Exception as e:
                self.photos_data.append({
                    "photo_path": photo_path,
                    "latitude": "Erreur",
                    "longitude": "Erreur",
                    "altitude": "Erreur",
                    "date": "Erreur"
                })

        # Afficher chaque photo et ses métadonnées
        for i, data in enumerate(self.photos_data):
            card = ttk.Frame(
                scrollable_frame,
                bootstyle="secondary",
                padding=20,
                relief="raised",
                borderwidth=2
            )
            card.pack(pady=15, padx=20, fill="x")

            content_frame = ttk.Frame(card)
            content_frame.pack(fill="x")

        # Image
            img_frame = ttk.Frame(content_frame)
            img_frame.pack(side="left", padx=(0, 25))
            try:
                img = Image.open(data["photo_path"])
                img.thumbnail((160, 160), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)

                img_label = ttk.Label(img_frame, image=img_tk)
                img_label.image = img_tk
                img_label.pack()

                badge_label = ttk.Label(
                    img_frame,
                    text=f"Photo {i+1}",
                    font=("Segoe UI", 9, "bold"),
                    bootstyle="info",
                    padding=5
                )
                badge_label.pack(pady=(5, 0))
            except:
                error_label = ttk.Label(
                    img_frame,
                    text="❌ Erreur de chargement",
                    font=("Segoe UI", 10),
                    bootstyle="danger",
                    justify="center"
                )
                error_label.pack(pady=40)

        # Infos
            info_frame = ttk.Frame(content_frame)
            info_frame.pack(side="left", fill="both", expand=True)

            filename = os.path.basename(data["photo_path"])
            name_label = ttk.Label(
                info_frame,
                text=f"📄 {filename}",
                font=("Segoe UI", 13, "bold"),
                bootstyle="light"
            )
            name_label.pack(anchor="w", pady=(0, 15))

            separator = ttk.Separator(info_frame, orient="horizontal")
            separator.pack(fill="x", pady=(0, 15))

            metadata_grid = ttk.Frame(info_frame)
            metadata_grid.pack(fill="x")

            self.add_metadata_row(metadata_grid, 0, "🌍 Latitude:", str(data["latitude"]))
            self.add_metadata_row(metadata_grid, 1, "🌍 Longitude:", str(data["longitude"]))
            self.add_metadata_row(metadata_grid, 2, "⛰️ Altitude:", str(data["altitude"]))
            self.add_metadata_row(metadata_grid, 3, "🕐 Date/Heure:", str(data["date"]))

       
        buttons_frame = ttk.Frame(main_container,style="Black.TFrame")
        buttons_frame.pack(fill="x", pady=(10, 0))

        
        btn_back = ttk.Button(
            buttons_frame,
            text="⬅️ Retour",
            bootstyle="secondary",
            command=self.go_back,
            width=20
        )
        btn_back.pack(side="left", ipady=10)

        
        btn_map = ttk.Button(
            buttons_frame,
            text="suivant",
            bootstyle="success",
            command=self.go_next,
            width=25
        )
        btn_map.pack(side="right", ipady=10)

    def add_metadata_row(self, parent, row, label_text, value_text):
        label = ttk.Label(
            parent,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            bootstyle="secondary"
        )
        label.grid(row=row, column=0, sticky="w", pady=5, padx=(0, 15))

        value = ttk.Label(
            parent,
            text=value_text,
            font=("Segoe UI", 10),
            bootstyle="light"
        )
        value.grid(row=row, column=1, sticky="w", pady=5)

    def go_back(self):
        self.pack_forget()
        self.switch_to_selection()

    def go_next(self):
        self.pack_forget()
        # ici tu prépares les coordonnées et tu passes à la fenetre Map
        self.switch_to_map()

        