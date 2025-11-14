import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from exif import Image as ExifImage    
import backend
class FenetreSelection(ttk.Frame):
    def __init__(self, master, switch_to_metadata):
        super().__init__(master)
        self.switch_to_metadata = switch_to_metadata
        self.photos = []
        self.photo_frames = []
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("Black.TFrame", background="black")
        main_container = ttk.Frame(self,style="Black.TFrame", padding=40)
        main_container.pack(fill="both", expand=True)

        
        header_frame = ttk.Frame(main_container,style="Black.TFrame")
        header_frame.pack(pady=(0, 40))
        
        title_label = ttk.Label(
            header_frame,
            text="📸 Sélection des Photos",
            font=("Segoe UI", 32, "bold"),
            bootstyle="light",
            background="black"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Choisissez 3 photos pour la géolocalisation",
            font=("Segoe UI", 12),
            bootstyle="secondary",
            background="black"
        )
        subtitle_label.pack(pady=(5, 0))

       
        self.preview_frame = ttk.Labelframe(
            main_container,
            text="  Photos sélectionnées  ",
            padding=20,
            bootstyle="info",
            
        )
        self.preview_frame.pack(fill="both", expand=True, pady=(0, 30))
        
        
        self.thumbnails_container = ttk.Frame(self.preview_frame)
        self.thumbnails_container.pack(fill="both", expand=True)
        
        
        self.empty_label = ttk.Label(
            self.thumbnails_container,
            text="🖼️ Aucune photo sélectionnée\n\nCliquez sur 'Parcourir' pour ajouter des photos",
            font=("Segoe UI", 11),
            bootstyle="secondary",
            justify="center"
        )
        self.empty_label.pack(expand=True)

        
        buttons_frame = ttk.Frame(main_container,style="Black.TFrame")
        buttons_frame.pack(fill="x")

        
        self.btn_select = ttk.Button(
            buttons_frame,
            text="📁 Parcourir",
            bootstyle="info",
            command=self.choisir_photos,
            width=20
        )
        self.btn_select.pack(side="left", padx=5, ipady=10)

        
        self.btn_clear = ttk.Button(
            buttons_frame,
            text="🗑️ Effacer",
            bootstyle="warning",
            command=self.Effacer,
            width=20
        )
        self.btn_clear.pack(side="left", padx=5, ipady=10)

        
        self.btn_submit = ttk.Button(
            buttons_frame,
            text="➡️ Suivant",
            bootstyle="success",
            command=self.submit,
            width=20
        )
        self.btn_submit.pack(side="right", padx=5, ipady=10)

        
        self.counter_label = ttk.Label(
            main_container,
            text="0 / 3 photos",
            font=("Segoe UI", 10),
            bootstyle="secondary"
        )
        self.counter_label.pack(pady=(10, 0))

    def choisir_photos(self):
        files = filedialog.askopenfilenames(
            title="Sélectionnez vos photos",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.JPG *.JPEG *.PNG")]
        )

        if not files:
            return

        # Valider les photos sélectionnées
        new_validated = []
        for f in files:
            with open(f, "rb") as img_file:
                img = ExifImage(img_file)
                if backend.verifier(img) and backend.verifier_gps(img):
                    new_validated.append(f)

        if not new_validated:
            messagebox.showwarning("Avertissement", "y a pas de données GPS dans la photo.")
            return

        # Ajouter les nouvelles photos aux photos existantes
        self.photos.extend(new_validated)

        self.update_preview()



    def Effacer(self):
        if self.photos:
            confirm = messagebox.askyesno(
                "Confirmation",
                "Voulez-vous vraiment effacer toutes les photos ?"
            )
            if confirm:
                self.photos = []
                self.update_preview()
        else:
            messagebox.showinfo("Information", "Aucune photo à effacer.")



    def update_preview(self):
        # Supprimer tout ce qui est déjà dans le container
        for widget in self.thumbnails_container.winfo_children():
            widget.destroy()

        if not self.photos:
            self.empty_label = ttk.Label(
                self.thumbnails_container,
                text="🖼️ Aucune photo sélectionnée\n\nCliquez sur 'Parcourir' pour ajouter des photos",
                font=("Segoe UI", 11),
                bootstyle="secondary",
                justify="center"
            )
            self.empty_label.pack(expand=True)
            self.counter_label.config(text="0 / 3 photos")
            return

        # Créer un frame pour la grille des miniatures
        grid_frame = ttk.Frame(self.thumbnails_container)
        grid_frame.pack(expand=True)

        for i, photo_path in enumerate(self.photos):
            card = ttk.Frame(grid_frame, bootstyle="secondary", relief="raised")
            card.grid(row=0, column=i, padx=15, pady=10)

            try:
                img = Image.open(photo_path)
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)

                img_label = ttk.Label(card, image=img_tk)
                img_label.image = img_tk  # garder référence pour Tkinter
                img_label.pack(padx=10, pady=10)

                filename = os.path.basename(photo_path)
                if len(filename) > 20:
                    filename = filename[:17] + "..."
                name_label = ttk.Label(
                    card,
                    text=filename,
                    font=("Segoe UI", 9),
                    bootstyle="light"
                )
                name_label.pack(pady=(0, 5))

                remove_btn = ttk.Button(
                    card,
                    text="✕",
                    bootstyle="danger-link",
                    command=lambda idx=i: self.remove_photo(idx),
                    width=3
                )   
                remove_btn.pack(pady=(0, 5))

            except Exception as e:
                error_label = ttk.Label(
                    card,
                    text="❌ Erreur\nchargement",
                    font=("Segoe UI", 9),
                    bootstyle="danger"
                    ,background="black"
                )
                error_label.pack(padx=20, pady=40)

        self.counter_label.config(text=f"{len(self.photos)} photos")


    def remove_photo(self, index):
        if 0 <= index < len(self.photos):
            self.photos.pop(index)
            self.update_preview()

    def submit(self):
        if len(self.photos) == 0:
            messagebox.showwarning(
                "Attention",
                "Veuillez sélectionner au moins une photo."
            )
        elif len(self.photos) < 3:
            confirm = messagebox.askyesno(
                "Confirmation",
                f"Vous avez sélectionné {len(self.photos)} photos.\n"
                "Il est recommandé de sélectionner exactement 3 photos.\n\n"
                "Voulez-vous continuer ?"
            )
            if confirm:

                self.switch_to_metadata(self.photos)
        else:

            self.switch_to_metadata(self.photos)