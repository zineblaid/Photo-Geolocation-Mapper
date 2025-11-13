import ttkbootstrap as ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tempfile
import os

class FenetreMap(ttk.Frame):
    def __init__(self, master, go_back_callback):
        super().__init__(master)
        self.go_back_callback = go_back_callback
        self.coords_list = []
        self.itinerary_visible = False
        self.map_frame = None
        self.main_container = None
        self.transport_mode = ttk.StringVar(value="walking")

    def afficher_carte(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.itinerary_visible = False

        # Canvas avec scrollbar
        canvas = ttk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        self.main_container = ttk.Frame(canvas, padding=20)
        
        self.main_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.main_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text="🗺️ Carte de Géolocalisation",
            font=("Segoe UI", 28, "bold"),
            bootstyle="light"
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            header_frame,
            text="Visualisation des positions GPS et du périmètre",
            font=("Segoe UI", 11),
            bootstyle="secondary"
        )
        subtitle_label.pack(pady=(5, 0))

        info_panel = ttk.Labelframe(
            self.main_container,
            text="  Informations du trajet  ",
            padding=15,
            bootstyle="info"
        )
        info_panel.pack(fill="x", pady=(0, 15))

        self.coords_list = [
            {"latitude": 36.7525, "longitude": 3.042, "name": "Photo 1"},
            {"latitude": 36.7535, "longitude": 3.045, "name": "Photo 2"},
            {"latitude": 36.7510, "longitude": 3.048, "name": "Photo 3"}
        ]

        avg_lat = sum(c["latitude"] for c in self.coords_list) / len(self.coords_list)
        avg_lon = sum(c["longitude"] for c in self.coords_list) / len(self.coords_list)
        
        distance_km = self.calculate_perimeter()

        stats_frame = ttk.Frame(info_panel)
        stats_frame.pack(fill="x")

        stats_data = [
            ("📍 Points GPS", f"{len(self.coords_list)} positions"),
            ("🎯 Centre", f"{avg_lat:.4f}°, {avg_lon:.4f}°"),
            ("📏 Périmètre", f"~{distance_km:.2f} km"),
            ("🌍 Zone", "Alger, Algérie")
        ]

        for i, (label, value) in enumerate(stats_data):
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.grid(row=0, column=i, padx=15, pady=5)

            ttk.Label(
                stat_frame,
                text=label,
                font=("Segoe UI", 9, "bold"),
                bootstyle="secondary"
            ).pack()

            ttk.Label(
                stat_frame,
                text=value,
                font=("Segoe UI", 10),
                bootstyle="light"
            ).pack()

        self.map_frame = ttk.Labelframe(
            self.main_container,
            text="  Carte interactive  ",
            padding=10,
            bootstyle="secondary"
        )
        self.map_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.generate_map(show_itinerary=False)

        transport_panel = ttk.Labelframe(
            self.main_container,
            text="  🚦 Mode de transport pour l'itinéraire  ",
            padding=12,
            bootstyle="primary"
        )
        transport_panel.pack(fill="x", pady=(0, 10))

        radio_frame = ttk.Frame(transport_panel)
        radio_frame.pack(fill="x", pady=5)

        radio_walking = ttk.Radiobutton(
            radio_frame,
            text="🚶 À pied",
            variable=self.transport_mode,
            value="walking",
            command=self.on_transport_change
        )
        radio_walking.pack(side="left", padx=15, ipady=8)

        radio_bike = ttk.Radiobutton(
            radio_frame,
            text="🚴 Vélo",
            variable=self.transport_mode,
            value="cycling",
            command=self.on_transport_change
        )
        radio_bike.pack(side="left", padx=15, ipady=8)

        radio_car = ttk.Radiobutton(
            radio_frame,
            text="🚗 Voiture",
            variable=self.transport_mode,
            value="driving",
            command=self.on_transport_change
        )
        radio_car.pack(side="left", padx=15, ipady=8)

        self.mode_indicator = ttk.Label(
            transport_panel,
            text="✅ Mode actuel : 🚶 À pied",
            font=("Segoe UI", 9, "bold"),
            bootstyle="success"
        )
        self.mode_indicator.pack(anchor="center", pady=(8, 0))

        buttons_frame = ttk.Frame(self.main_container)
        buttons_frame.pack(fill="x")

        btn_back = ttk.Button(
            buttons_frame,
            text="⬅️ Retour",
            bootstyle="secondary",
            command=self.go_back_callback,
            width=20
        )
        btn_back.pack(side="left", ipady=10)

        self.btn_route = ttk.Button(
            buttons_frame,
            text="🚶 Afficher l'itinéraire",
            bootstyle="success",
            command=self.toggle_itinerary,
            width=25
        )
        self.btn_route.pack(side="left", padx=10, ipady=10)

        btn_export = ttk.Button(
            buttons_frame,
            text="💾 Exporter la carte",
            bootstyle="info",
            command=self.export_map,
            width=20
        )
        btn_export.pack(side="right", ipady=10)

    def on_transport_change(self):
        mode = self.transport_mode.get()
        mode_labels = {
            "walking": ("🚶 À pied", "success"),
            "cycling": ("🚴 Vélo", "info"),
            "driving": ("🚗 Voiture", "warning")
        }
        
        label, style = mode_labels[mode]
        self.mode_indicator.config(text=f"✅ Mode actuel : {label}", bootstyle=style)
        
        if self.itinerary_visible:
            self.generate_map(show_itinerary=True)

    def generate_map(self, show_itinerary=False):
        for widget in self.map_frame.winfo_children():
            widget.destroy()

        try:
            width, height = 800, 500
            img = Image.new('RGB', (width, height), color='#e8f4f8')
            draw = ImageDraw.Draw(img)
            
            for i in range(0, width, 50):
                draw.line([(i, 0), (i, height)], fill='#d0e8f0', width=1)
            for i in range(0, height, 50):
                draw.line([(0, i), (width, i)], fill='#d0e8f0', width=1)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 24)
                subtitle_font = ImageFont.truetype("arial.ttf", 14)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            draw.text((width//2 - 150, 30), "🗺️ CARTE DE GÉOLOCALISATION", fill='#2c3e50', font=title_font)
            
            
            if self.coords_list:
                lats = [c["latitude"] for c in self.coords_list]
                lons = [c["longitude"] for c in self.coords_list]
                
                min_lat, max_lat = min(lats), max(lats)
                min_lon, max_lon = min(lons), max(lons)
                
                lat_range = max_lat - min_lat if max_lat != min_lat else 0.001
                lon_range = max_lon - min_lon if max_lon != min_lon else 0.001
                
                padding = 100
                map_width = width - 2 * padding
                map_height = height - 2 * padding - 100
                
                points = []
                colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
                
                for i, coord in enumerate(self.coords_list):
                    x = padding + int((coord["longitude"] - min_lon) / lon_range * map_width)
                    y = height - padding - 50 - int((coord["latitude"] - min_lat) / lat_range * map_height)
                    points.append((x, y))
                    
                    marker_size = 20
                    color = colors[i % len(colors)]
                    
                    draw.ellipse([x-marker_size, y-marker_size, x+marker_size, y+marker_size], 
                                fill=color, outline='#2c3e50', width=3)
                    
                    try:
                        marker_font = ImageFont.truetype("arial.ttf", 16)
                    except:
                        marker_font = ImageFont.load_default()
                    
                    text = str(i + 1)
                    bbox = draw.textbbox((0, 0), text, font=marker_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    draw.text((x - text_width//2, y - text_height//2 - 2), text, 
                             fill='white', font=marker_font)
                    
                    label = coord["name"]
                    label_y = y + marker_size + 10
                    bbox = draw.textbbox((0, 0), label, font=subtitle_font)
                    label_width = bbox[2] - bbox[0]
                    draw.rectangle([x - label_width//2 - 5, label_y - 5, 
                                  x + label_width//2 + 5, label_y + 15], 
                                 fill='white', outline=color, width=2)
                    draw.text((x - label_width//2, label_y), label, fill='#2c3e50', font=subtitle_font)
                
                if len(points) >= 3:
                    for i in range(len(points)):
                        start = points[i]
                        end = points[(i + 1) % len(points)]
                        draw.line([start, end], fill='#3498db', width=2)
                
                if show_itinerary and len(points) >= 2:
                    mode = self.transport_mode.get()
                    transport_colors = {
                        "walking": ("#27ae60", "À pied"),
                        "cycling": ("#3498db", "Vélo"),
                        "driving": ("#e67e22", "Voiture")
                    }
                    
                    line_color, mode_name = transport_colors[mode]
                    
                    for i in range(len(points) - 1):
                        start = points[i]
                        end = points[i + 1]
                        
                        draw.line([start, end], fill=line_color, width=5)
                        
                        mid_x = (start[0] + end[0]) // 2
                        mid_y = (start[1] + end[1]) // 2
                        
                        arrow_size = 12
                        draw.polygon([
                            (mid_x, mid_y - arrow_size),
                            (mid_x - arrow_size, mid_y + arrow_size),
                            (mid_x + arrow_size, mid_y + arrow_size)
                        ], fill=line_color, outline='#2c3e50', width=2)
                
                legend_y = height - 90
                legend_height = 70 if show_itinerary else 50
                draw.rectangle([20, legend_y, 320, height - 20], fill='white', outline='#34495e', width=2)
                
                draw.text((30, legend_y + 10), "📍 Marqueurs = Positions GPS", fill='#2c3e50', font=subtitle_font)
                draw.text((30, legend_y + 30), "🔵 Ligne bleue = Périmètre", fill='#2c3e50', font=subtitle_font)
                
                if show_itinerary:
                    mode = self.transport_mode.get()
                    mode_icons = {
                        "walking": "🚶",
                        "cycling": "🚴",
                        "driving": "🚗"
                    }
                    icon = mode_icons[mode]
                    draw.text((30, legend_y + 50), f"{icon} Itinéraire ({mode_name})", fill='#2c3e50', font=subtitle_font)
            
            else:
                draw.text((width//2 - 100, height//2), "Aucune donnée GPS disponible", 
                         fill='#95a5a6', font=title_font)
            
            photo = ImageTk.PhotoImage(img)
            
            map_label = ttk.Label(self.map_frame, image=photo)
            map_label.image = photo
            map_label.pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            error_label = ttk.Label(
                self.map_frame,
                text=f"❌ Erreur lors du chargement de la carte\n{str(e)}",
                font=("Segoe UI", 12),
                bootstyle="danger",
                justify="center"
            )
            error_label.pack(expand=True)

    def toggle_itinerary(self):
        self.itinerary_visible = not self.itinerary_visible
        
        if self.itinerary_visible:
            mode = self.transport_mode.get()
            mode_names = {
                "walking": "À pied 🚶",
                "cycling": "Vélo 🚴",
                "driving": "Voiture 🚗"
            }
            
            self.btn_route.config(text="🚫 Masquer l'itinéraire")
            self.generate_map(show_itinerary=True)
            messagebox.showinfo(
                "Itinéraire", 
                f"L'itinéraire a été tracé sur la carte!\n\nMode: {mode_names[mode]}"
            )
        else:
            self.btn_route.config(text="🚶 Afficher l'itinéraire")
            self.generate_map(show_itinerary=False)

    def calculate_perimeter(self):
        if len(self.coords_list) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(self.coords_list)):
            c1 = self.coords_list[i]
            c2 = self.coords_list[(i + 1) % len(self.coords_list)]
            
            lat_diff = abs(c1["latitude"] - c2["latitude"])
            lon_diff = abs(c1["longitude"] - c2["longitude"])
            distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
            total_distance += distance
        
        return total_distance

    def show_route(self):
        route_info = "📍 Détails de l'itinéraire:\n\n"
        for i, coord in enumerate(self.coords_list, 1):
            route_info += f"Étape {i}: {coord['name']}\n"
            route_info += f"  📌 {coord['latitude']}, {coord['longitude']}\n"
            if i < len(self.coords_list):
                route_info += f"  ↓\n"
        
        route_info += f"\n📏 Distance totale: ~{self.calculate_perimeter():.2f} km"
        
        messagebox.showinfo("Détails de l'itinéraire", route_info)

    def export_map(self):
        messagebox.showinfo(
            "Export", 
            "Fonction d'export disponible avec le backend.\n\n"
            "La carte interactive sera exportée en format HTML."
        )