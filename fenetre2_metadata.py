import ttkbootstrap as ttk
from PIL import Image, ImageTk
import os

class FenetreMetadata(ttk.Frame):
    def __init__(self, master, switch_to_map):
        super().__init__(master)
        self.switch_to_map = switch_to_map
        self.photos_data = []

    def afficher_photos(self, photos):
        for widget in self.winfo_children():
            widget.destroy()

        
        main_container = ttk.Frame(self, padding=30)
        main_container.pack(fill="both", expand=True)

        
        header_frame = ttk.Frame(main_container)
        header_frame.pack(pady=(0, 30))
        
        title_label = ttk.Label(
            header_frame,
            text="📋 Métadonnées GPS",
            font=("Segoe UI", 32, "bold"),
            bootstyle="light"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Informations de géolocalisation extraites des photos",
            font=("Segoe UI", 12),
            bootstyle="secondary"
        )
        subtitle_label.pack(pady=(5, 0))

        
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

        
        fake_coords = [
            {"latitude": 36.7525, "longitude": 3.042, "altitude": 25, "date": "2024-11-10 14:30"},
            {"latitude": 36.7535, "longitude": 3.045, "altitude": 30, "date": "2024-11-10 15:15"},
            {"latitude": 36.7510, "longitude": 3.048, "altitude": 22, "date": "2024-11-10 16:00"}
        ]

       
        for i, photo_path in enumerate(photos):
            
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

            
            img_frame = ttk.Frame(content_frame)
            img_frame.pack(side="left", padx=(0, 25))

            try:
                img = Image.open(photo_path)
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

            except Exception as e:
                error_label = ttk.Label(
                    img_frame,
                    text="❌ Erreur de\nchargement",
                    font=("Segoe UI", 10),
                    bootstyle="danger",
                    justify="center"
                )
                error_label.pack(pady=40)

            
            info_frame = ttk.Frame(content_frame)
            info_frame.pack(side="left", fill="both", expand=True)

            
            filename = os.path.basename(photo_path)
            name_label = ttk.Label(
                info_frame,
                text=f"📄 {filename}",
                font=("Segoe UI", 13, "bold"),
                bootstyle="light"
            )
            name_label.pack(anchor="w", pady=(0, 15))

           
            separator = ttk.Separator(info_frame, orient="horizontal")
            separator.pack(fill="x", pady=(0, 15))

            
            if i < len(fake_coords):
                coord = fake_coords[i]
                
                metadata_grid = ttk.Frame(info_frame)
                metadata_grid.pack(fill="x")

                
                self.add_metadata_row(metadata_grid, 0, "🌍 Latitude:", f"{coord['latitude']}°")
                
                
                self.add_metadata_row(metadata_grid, 1, "🌍 Longitude:", f"{coord['longitude']}°")
                
                
                self.add_metadata_row(metadata_grid, 2, "⛰️ Altitude:", f"{coord['altitude']} m")
                
               
                self.add_metadata_row(metadata_grid, 3, "🕐 Date/Heure:", coord['date'])

            else:
                no_data_label = ttk.Label(
                    info_frame,
                    text="⚠️ Aucune donnée GPS disponible",
                    font=("Segoe UI", 11),
                    bootstyle="warning"
                )
                no_data_label.pack(anchor="w")

       
        buttons_frame = ttk.Frame(main_container)
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
            text="🗺️ Afficher la Carte",
            bootstyle="success",
            command=self.switch_to_map,
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
        