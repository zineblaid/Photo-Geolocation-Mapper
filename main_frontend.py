import ttkbootstrap as ttk
from fenetre1_selection import FenetreSelection
from fenetre2_metadata import FenetreMetadata
from fenetre3_map import FenetreMap

class Application(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("🌍 Projet Géolocalisation GPS")
        self.geometry("1100x750")
        self.resizable(True, True)
        
        self.center_window()
        
        self.f1 = FenetreSelection(self, self.go_to_metadata)
        self.f2 = FenetreMetadata(self, self.go_to_map)
        self.f3 = FenetreMap(self, self.go_to_metadata_from_map)
        
        self.current_photos = []
        
        self.f1.pack(fill="both", expand=True)
        
        self.create_menu()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_menu(self):
        menubar = ttk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = ttk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouvelle analyse", command=self.reset_to_start)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit)
        
        help_menu = ttk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)

    def go_to_metadata(self, photos):
        self.current_photos = photos
        self.f1.pack_forget()
        self.f2.pack(fill="both", expand=True)
        self.f2.afficher_photos(photos)

    def go_to_map(self):
        self.f2.pack_forget()
        self.f3.pack(fill="both", expand=True)
        self.f3.afficher_carte()

    def go_to_metadata_from_map(self):
        self.f3.pack_forget()
        self.f2.pack(fill="both", expand=True)

    def reset_to_start(self):
        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous recommencer une nouvelle analyse?\nLes données actuelles seront perdues."
        )
        if confirm:
            self.f2.pack_forget()
            self.f3.pack_forget()
            
            self.f1.photos = []
            self.f1.update_preview()
            
            self.f1.pack(fill="both", expand=True)

    def show_about(self):
        from tkinter import messagebox
        messagebox.showinfo(
            "À propos",
            "🌍 Application de Géolocalisation GPS\n\n"
            "Développé pour l'extraction et la visualisation\n"
            "des métadonnées GPS à partir de photos.\n\n"
            "© 2025 - Projet Universitaire"
        )

if __name__ == "__main__":
    app = Application()
    app.mainloop()