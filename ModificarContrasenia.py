import tkinter as tk
from tkinter import messagebox


class VentanaModificarContrasenia:
    def __init__(self, parent, cursor, conexion, telefono):
        self.cursor = cursor
        self.conexion = conexion
        self.telefono = telefono

        self.window = tk.Toplevel(parent)
        self.window.title("Modificar Contraseña")
        self.window.geometry("400x200")
        self.window.configure(bg="#E3F2FD")

        tk.Label(self.window, text=f"Número: {telefono}", font=("Arial", 12, "bold"), bg="#E3F2FD"
                 ).pack(pady=(20, 10))

        tk.Label(self.window, text="Nueva Contraseña:", font=("Arial", 12), bg="#E3F2FD"
                 ).pack(pady=5)
        self.entrada_clave = tk.Entry(self.window, show="*", font=("Arial", 12), width=30)
        self.entrada_clave.pack(pady=5)

        tk.Button(self.window, text="Actualizar", font=("Arial", 12), bg="#64B5F6",
                  command=self.actualizar_clave).pack(pady=15)

    def actualizar_clave(self):
        nueva_clave = self.entrada_clave.get().strip()
        if not nueva_clave:
            messagebox.showwarning("Advertencia", "La contraseña no puede estar vacía.")
            return

        try:
            self.cursor.execute("UPDATE loginVendedor SET clave = %s WHERE numTelV = %s", (nueva_clave, self.telefono))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la contraseña: {str(e)}")
