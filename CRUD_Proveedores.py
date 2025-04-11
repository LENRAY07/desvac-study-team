import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


class ProveedoresApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proveedores")
        self.root.geometry("1000x600")
        self.root.configure(bg="#5bfcfe")

        # Variables de estado
        self.modo_edicion = False
        self.proveedor_seleccionado = None
        self.clave_original = None

        # Conexión a MySQL
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="dbtiendaletty"
        )
        self.cursor = self.conexion.cursor()

        self.crear_interfaz()
        self.crear_tabla_proveedores()
        self.mostrar_proveedores()

    def crear_tabla_proveedores(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS proveedores (
                    clave CHAR(12) PRIMARY KEY,
                    numTelProv CHAR(10),
                    empresa VARCHAR(30)
                    )
            """)
            self.conexion.commit()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la tabla: {str(e)}")

    def crear_interfaz(self):
        # Configuración de grid
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=3)

        # Configurar filas
        for i in range(6):
            self.root.grid_rowconfigure(i, weight=0)
        self.root.grid_rowconfigure(6, weight=1)

        # Título
        tk.Label(self.root, text="Proveedores", font=("Impact", 20, "bold"), bg="#5bfcfe"
                 ).grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

        # Campos de entrada
        self.campos = {}
        campos_config = [
            ("Clave:", "clave", ""),
            ("Teléfono:", "numTelProv", ""),
            ("Empresa:", "empresa", "")
        ]

        for i, (texto, nombre, show_char) in enumerate(campos_config, start=1):
            tk.Label(self.root, text=texto, font=("Arial", 14), bg="#5bfcfe"
                     ).grid(row=i, column=0, padx=10, pady=10, sticky="w")

            entry = tk.Entry(self.root, font=("Arial", 14), bg="#e6ffff", show=show_char)
            entry.grid(row=i, column=2, padx=(0, 20), pady=10, sticky="ew")
            self.campos[nombre] = entry

        # Frame para botones principales
        frame_botones_principales = tk.Frame(self.root, bg="#5bfcfe")
        frame_botones_principales.grid(row=5, column=0, columnspan=3, pady=20)

        # Botones CRUD principales
        self.btn_crear = tk.Button(frame_botones_principales, text="Crear", bg="#A2E4B8",
                                   font=("Arial", 12), command=self.crear_proveedor)
        self.btn_crear.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)

        self.btn_leer = tk.Button(frame_botones_principales, text="Leer", bg="#9AD0F5",
                                  font=("Arial", 12), command=self.mostrar_detalles_proveedor)
        self.btn_leer.grid(row=0, column=1, padx=10, ipadx=10, ipady=5)

        self.btn_editar = tk.Button(frame_botones_principales, text="Editar", bg="#FFE08A",
                                    font=("Arial", 12), command=self.preparar_edicion)
        self.btn_editar.grid(row=0, column=2, padx=10, ipadx=10, ipady=5)

        self.btn_borrar = tk.Button(frame_botones_principales, text="Borrar", bg="#F4A4A4",
                                    font=("Arial", 12), command=self.borrar_proveedor)
        self.btn_borrar.grid(row=0, column=3, padx=10, ipadx=10, ipady=5)

        # Frame para botones secundarios (confirmar/cancelar/volver)
        self.frame_botones_secundarios = tk.Frame(self.root, bg="#5bfcfe")
        self.frame_botones_secundarios.grid(row=7, column=0, columnspan=3, pady=10)
        self.frame_botones_secundarios.grid_remove()  # Ocultar inicialmente

        self.btn_confirmar = tk.Button(self.frame_botones_secundarios, text="Confirmar", bg="#A2E4B8",
                                       font=("Arial", 12), command=self.confirmar_actualizacion)
        self.btn_confirmar.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)

        self.btn_cancelar = tk.Button(self.frame_botones_secundarios, text="Cancelar", bg="#F4A4A4",
                                      font=("Arial", 12), command=self.cancelar_edicion)
        self.btn_cancelar.grid(row=0, column=1, padx=10, ipadx=10, ipady=5)

        self.btn_volver = tk.Button(self.frame_botones_secundarios, text="Volver a lista", bg="#9AD0F5",
                                    font=("Arial", 12), command=self.volver_a_lista)
        self.btn_volver.grid(row=0, column=2, padx=10, ipadx=10, ipady=5)

        # Treeview
        frame_tabla = tk.Frame(self.root)
        frame_tabla.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))

        self.tabla = ttk.Treeview(frame_tabla, columns=("Clave", ), show="headings")
        self.tabla.heading("Clave", text="Clave")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mostrar_proveedores(self):
        """Muestra todos los proveedores en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            self.cursor.execute("SELECT clave FROM proveedores ORDER BY empresa")
            proveedores = self.cursor.fetchall()

            for proveedor in proveedores:
                self.tabla.insert("", "end", values=proveedor)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los proveedores: {str(e)}")

    def crear_proveedor(self):
        """Crea un nuevo proveedor"""
        datos = {
            'clave': self.campos['clave'].get(),
            'numTelProv': self.campos['numTelProv'].get(),
            'empresa': self.campos['empresa'].get()
        }

        # Validación básica
        if not datos['clave']:
            messagebox.showwarning("Advertencia", "La clave es un campo obligatorio")
            return

        try:
            self.cursor.execute("""
                INSERT INTO proveedores (clave, numTelProv, empresa)
                VALUES (%s, %s, %s)
            """, (datos['clave'], datos['numTelProv'], datos['empresa']))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Proveedor creado correctamente")
            self.volver_a_lista()
            self.limpiar_campos()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "La clave ya existe")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el proveedor: {str(e)}")

    def mostrar_detalles_proveedor(self):
        """Muestra los detalles del proveedor seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor primero")
            return

        clave = self.tabla.item(seleccion[0])['values'][0]

        try:
            self.cursor.execute("SELECT * FROM proveedores WHERE clave = %s", (clave,))
            proveedor = self.cursor.fetchone()

            if proveedor:
                # Configurar columnas para mostrar detalles
                self.tabla["columns"] = ("Clave", "Teléfono", "Empresa")

                # Configurar encabezados
                columnas = [
                    ("Clave", 150),
                    ("Teléfono", 150),
                    ("Empresa", 250)
                ]

                for col, width in columnas:
                    self.tabla.heading(col, text=col)
                    self.tabla.column(col, width=width)

                # Limpiar tabla y mostrar solo este proveedor
                for item in self.tabla.get_children():
                    self.tabla.delete(item)

                self.tabla.insert("", "end", values=proveedor)
                self.proveedor_seleccionado = proveedor

                # Mostrar botón "Volver a lista"
                self.frame_botones_secundarios.grid()
                self.btn_volver.config(state=tk.NORMAL)
                self.btn_confirmar.config(state=tk.DISABLED)
                self.btn_cancelar.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Información", "No se encontraron detalles para este proveedor")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles: {str(e)}")

    def preparar_edicion(self):
        """Prepara la interfaz para editar un proveedor"""
        if not self.proveedor_seleccionado:
            messagebox.showwarning("Advertencia", "Primero use 'Leer' en un proveedor")
            return

        # Cargar datos en los campos
        self.limpiar_campos()
        self.campos['clave'].insert(0, self.proveedor_seleccionado[0])
        self.campos['numTelProv'].insert(0, self.proveedor_seleccionado[1] or "")
        self.campos['empresa'].insert(0, self.proveedor_seleccionado[2] or "")

        # Deshabilitar campo de clave (es la clave primaria)
        self.campos['clave'].config(state='disabled')

        # Cambiar a modo edición
        self.modo_edicion = True
        self.clave_original = self.proveedor_seleccionado[0]

        # Mostrar botones de confirmación
        self.frame_botones_secundarios.grid()
        self.btn_confirmar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.NORMAL)
        self.btn_volver.config(state=tk.DISABLED)

        # Deshabilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.DISABLED)

    def confirmar_actualizacion(self):
        """Confirma la actualización del proveedor"""
        datos = {
            'clave_original': self.clave_original,
            'numTelProv': self.campos['numTelProv'].get(),
            'empresa': self.campos['empresa'].get()
        }

        try:
            # Actualizar el proveedor
            self.cursor.execute("""
                UPDATE proveedores 
                SET numTelProv = %s, empresa = %s
                WHERE clave = %s
            """, (datos['numTelProv'], datos['empresa'], datos['clave_original']))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Proveedor actualizado correctamente")
            self.cancelar_edicion()
            self.volver_a_lista()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el proveedor: {str(e)}")

    def cancelar_edicion(self):
        """Cancela el modo de edición"""
        # Limpiar todos los campos, incluyendo la clave (aunque esté deshabilitado)
        for nombre, campo in self.campos.items():
            campo.config(state='normal')  # Habilitar temporalmente para limpiar
            campo.delete(0, tk.END)

        self.modo_edicion = False
        self.clave_original = None

        # Ocultar botones secundarios
        self.frame_botones_secundarios.grid_remove()

        # Habilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.NORMAL)

    def volver_a_lista(self):
        self.tabla["columns"] = ("Clave")
        self.tabla.heading("Clave", text="Clave")
        self.tabla.column("Clave", width=200)
        """Vuelve a mostrar la lista de proveedores"""
        self.mostrar_proveedores()
        self.proveedor_seleccionado = None
        self.frame_botones_secundarios.grid_remove()

        # Habilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.NORMAL)

    def borrar_proveedor(self):
        """Borra un proveedor existente"""
        if not self.proveedor_seleccionado:
            messagebox.showwarning("Advertencia", "Primero use 'Leer' en un proveedor")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de borrar este proveedor?"):
            try:
                self.cursor.execute("DELETE FROM proveedores WHERE clave = %s", (self.proveedor_seleccionado[0],))
                self.conexion.commit()
                messagebox.showinfo("Éxito", "Proveedor borrado correctamente")
                self.volver_a_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar el proveedor: {str(e)}")

    def limpiar_campos(self):
        """Limpia todos los campos de entrada, incluso los deshabilitados"""
        for nombre, campo in self.campos.items():
            estado_actual = campo['state']  # Guardar estado actual
            campo.config(state='normal')  # Habilitar temporalmente
            campo.delete(0, tk.END)  # Limpiar contenido
            campo.config(state=estado_actual)  # Restaurar estado original

    def __del__(self):
        """Cierra la conexión a la base de datos al salir"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conexion'):
            self.conexion.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ProveedoresApp(root)
    root.mainloop()