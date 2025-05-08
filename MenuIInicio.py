import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class InicioApp:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app
        self.configurar_ventana_inicio()

    def configurar_ventana_inicio(self):
        # Frame de bienvenida
        welcome_frame = tk.Frame(self.root, bg="#2c3e50")
        welcome_frame.pack(expand=True, fill="both")

        # Label vacío para fondo extendido
        title_bg = tk.Label(welcome_frame, text="", bg="#2c3e50")
        title_bg.pack(fill="x")

        # Mensaje de bienvenida
        tk.Label(welcome_frame, text="Sistema de Gestión Tienda Letty",
                 font=("Segoe UI", 18, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=20)

        # Cargar y mostrar la imagen
        self.mostrar_imagen(welcome_frame)

    def mostrar_imagen(self, parent_frame):
        # Carga la imagen
        try:
            imagen = Image.open("C:/Users/xbox3/PyCharmMiscProject/logoprincipal.jpg")
            imagen = imagen.resize((626, 485), Image.LANCZOS)
            self.imagen_tk = ImageTk.PhotoImage(imagen)  # Convierte la imagen a un formato que Tkinter puede usar

            # Crea un Label para mostrar la imagen
            imagen_label = tk.Label(parent_frame, image=self.imagen_tk, bg="#2c3e50")
            imagen_label.pack(pady=20)  # Añade un poco de espacio alrededor de la imagen
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")

    def aclarar_color(self, color_hex, cantidad=30):
        """Aclara un color hexadecimal para efecto hover"""
        try:
            r = min(255, int(color_hex[1:3], 16) + cantidad)
            g = min(255, int(color_hex[3:5], 16) + cantidad)
            b = min(255, int(color_hex[5:7], 16) + cantidad)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color_hex








