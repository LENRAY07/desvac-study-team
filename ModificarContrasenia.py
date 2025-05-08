import tkinter as tk
from tkinter import messagebox, ttk


class VentanaModificarContrasenia:
    def __init__(self, parent, cursor, conexion, telefono):
        self.cursor = cursor
        self.conexion = conexion
        self.telefono = telefono

        self.window = tk.Toplevel(parent)
        self.window.title("Modificar Contraseña")
        self.window.geometry("400x250")
        self.window.resizable(False, False)
        self.window.configure(bg="#f0f2f5")

        # Aplicar el mismo estilo que la ventana principal
        self.style = ttk.Style()
        self.style.configure('TLabel', background="#f0f2f5", font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), relief="flat")

        # Frame principal
        main_frame = tk.Frame(self.window, bg="#f0f2f5", padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Encabezado
        header_frame = tk.Frame(main_frame, bg="#2c3e50", height=50)
        header_frame.pack(fill="x", pady=(0, 15))

        tk.Label(header_frame, text="Modificar Contraseña",
                 font=("Segoe UI", 14, "bold"),
                 bg="#2c3e50", fg="white").pack(side="left", padx=15)

        # Información del vendedor
        tk.Label(main_frame, text=f"Vendedor: {telefono}",
                 font=("Segoe UI", 11),
                 bg="#f0f2f5", fg="#2c3e50").pack(pady=(0, 15))

        # Campo de contraseña
        pass_frame = tk.Frame(main_frame, bg="#f0f2f5")
        pass_frame.pack(fill="x", pady=5)

        tk.Label(pass_frame, text="Nueva Contraseña:",
                 font=("Segoe UI", 11),
                 bg="#f0f2f5", fg="#2c3e50").pack(side="left", padx=(0, 10))

        self.entrada_clave = tk.Entry(pass_frame, show="*",
                                      font=("Segoe UI", 11),
                                      bd=2, relief="groove",
                                      highlightthickness=0)
        self.entrada_clave.pack(side="left", expand=True, fill="x")

        # Botón de actualizar
        btn_actualizar = tk.Button(main_frame, text="Actualizar Contraseña",
                                   font=("Segoe UI", 11, "bold"),
                                   bg="#27ae60", fg="white",
                                   activebackground="#2ecc71",
                                   activeforeground="white",
                                   relief="flat", bd=0,
                                   command=self.actualizar_clave)
        btn_actualizar.pack(pady=15, ipadx=20, ipady=5)

        # Efecto hover para el botón
        btn_actualizar.bind("<Enter>", lambda e: btn_actualizar.config(bg="#2ecc71"))
        btn_actualizar.bind("<Leave>", lambda e: btn_actualizar.config(bg="#27ae60"))

        # Centrar ventana
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def actualizar_clave(self):
        nueva_clave = self.entrada_clave.get().strip()
        if not nueva_clave:
            messagebox.showwarning("Advertencia", "La contraseña no puede estar vacía.")
            return

        try:
            self.cursor.execute("UPDATE loginVendedor SET clave = %s WHERE numTelV = %s",
                                (nueva_clave, self.telefono))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la contraseña: {str(e)}")
