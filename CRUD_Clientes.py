import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


class ClientesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clientes")
        self.root.geometry("1000x600")
        self.root.configure(bg="#5bfcfe")

        # Variables de estado
        self.modo_edicion = False
        self.cliente_seleccionado = None

        # Conexión a MySQL
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="dbtiendaletty"
        )
        self.cursor = self.conexion.cursor()

        self.crear_interfaz()
        self.crear_tabla_clientes()
        self.mostrar_nombres()

    def crear_tabla_clientes(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS cliente (
                    numTelC CHAR(10) PRIMARY KEY,
                    nombreC VARCHAR(50),
                    correo VARCHAR(50),
                    clave VARCHAR(50)
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
        for i in range(8):
            self.root.grid_rowconfigure(i, weight=0)
        self.root.grid_rowconfigure(8, weight=1)

        # Título
        tk.Label(self.root, text="Clientes", font=("Impact", 20, "bold"), bg="#5bfcfe"
                 ).grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

        # Campos de entrada
        self.campos = {}
        campos_config = [
            ("Teléfono:", "numTelC", ""),
            ("Nombre:", "nombreC", ""),
            ("Correo:", "correo", ""),
            ("Clave:", "clave", "*")
        ]

        for i, (texto, nombre, show_char) in enumerate(campos_config, start=1):
            tk.Label(self.root, text=texto, font=("Arial", 14), bg="#5bfcfe"
                     ).grid(row=i, column=0, padx=10, pady=10, sticky="w")

            entry = tk.Entry(self.root, font=("Arial", 14), bg="#e6ffff", show=show_char)
            entry.grid(row=i, column=2, padx=(0, 20), pady=10, sticky="ew")
            self.campos[nombre] = entry

        # Botones CRUD principales
        frame_botones = tk.Frame(self.root, bg="#5bfcfe")
        frame_botones.grid(row=5, column=0, columnspan=3, pady=10)

        self.botones_principales = [
            ("Crear", "#A2E4B8", self.crear_cliente),
            ("Leer", "#9AD0F5", self.mostrar_detalles_cliente),
            ("Editar", "#FFE08A", self.preparar_edicion),
            ("Borrar", "#F4A4A4", self.borrar_cliente)
        ]

        for i, (texto, color, comando) in enumerate(self.botones_principales):
            btn = tk.Button(frame_botones, text=texto, bg=color, font=("Arial", 12), command=comando)
            btn.grid(row=0, column=i, padx=5, ipadx=5, ipady=3)
            setattr(self, f"btn_{texto.lower()}", btn)

        # Botones de acción secundarios (inicialmente ocultos)
        frame_botones_secundarios = tk.Frame(self.root, bg="#5bfcfe")
        frame_botones_secundarios.grid(row=6, column=0, columnspan=3, pady=5)
        frame_botones_secundarios.grid_remove()

        self.btn_confirmar = tk.Button(
            frame_botones_secundarios, text="Confirmar", bg="#4CAF50", font=("Arial", 12),
            command=self.confirmar_actualizacion
        )
        self.btn_confirmar.grid(row=0, column=0, padx=5, ipadx=5, ipady=3)

        self.btn_cancelar = tk.Button(
            frame_botones_secundarios, text="Cancelar", bg="#F44336", font=("Arial", 12),
            command=self.cancelar_edicion
        )
        self.btn_cancelar.grid(row=0, column=1, padx=5, ipadx=5, ipady=3)

        self.btn_volver = tk.Button(
            frame_botones_secundarios, text="Volver a lista", bg="#2196F3", font=("Arial", 12),
            command=self.volver_a_lista
        )
        self.btn_volver.grid(row=0, column=2, padx=5, ipadx=5, ipady=3)

        self.frame_botones_secundarios = frame_botones_secundarios

        # Frame para la tabla de clientes
        frame_tabla = tk.Frame(self.root)
        frame_tabla.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))

        # Treeview para mostrar clientes
        self.tabla = ttk.Treeview(frame_tabla, columns=("Nombre",), show="headings")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.column("Nombre", width=300)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Posicionamiento
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mostrar_nombres(self):
        """Muestra solo los nombres de los clientes"""
        self.tabla["columns"] = ("Nombre",)
        self.tabla.heading("Nombre", text="Nombre")

        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            self.cursor.execute("SELECT nombreC FROM cliente ORDER BY nombreC")
            nombres = self.cursor.fetchall()

            for nombre in nombres:
                self.tabla.insert("", "end", values=nombre)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los nombres: {str(e)}")

    def mostrar_detalles_cliente(self):
        """Muestra los detalles del cliente seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un cliente primero")
            return

        nombre = self.tabla.item(seleccion[0])['values'][0]

        try:
            self.cursor.execute("SELECT * FROM cliente WHERE nombreC = %s", (nombre,))
            cliente = self.cursor.fetchone()

            if cliente:
                # Configurar columnas para mostrar detalles
                self.tabla["columns"] = ("Teléfono", "Nombre", "Correo", "Clave")

                # Configurar encabezados
                columnas = [
                    ("Teléfono", 120),
                    ("Nombre", 200),
                    ("Correo", 200),
                    ("Clave", 100)
                ]

                for col, width in columnas:
                    self.tabla.heading(col, text=col)
                    self.tabla.column(col, width=width)

                # Limpiar tabla y mostrar solo este cliente
                for item in self.tabla.get_children():
                    self.tabla.delete(item)

                self.tabla.insert("", "end", values=cliente)
                self.cliente_seleccionado = cliente

                # Mostrar botón "Volver a lista"
                self.frame_botones_secundarios.grid()
                self.btn_volver.config(state=tk.NORMAL)
            else:
                messagebox.showinfo("Información", "No se encontraron detalles para este cliente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles: {str(e)}")

    def preparar_edicion(self):
        """Prepara la interfaz para editar un cliente"""
        if not self.cliente_seleccionado:
            messagebox.showwarning("Advertencia", "Primero use 'Leer' en un cliente")
            return

        # Cargar datos en los campos
        self.limpiar_campos()
        self.campos['numTelC'].insert(0, self.cliente_seleccionado[0])
        self.campos['nombreC'].insert(0, self.cliente_seleccionado[1])
        self.campos['correo'].insert(0, self.cliente_seleccionado[2] or "")
        self.campos['clave'].insert(0, self.cliente_seleccionado[3] or "")

        # Cambiar a modo edición
        self.modo_edicion = True
        self.telefono_original = self.cliente_seleccionado[0]  # Guardamos el teléfono original

        # Mostrar botones de confirmación
        self.frame_botones_secundarios.grid()
        self.btn_confirmar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.NORMAL)
        self.btn_volver.config(state=tk.DISABLED)

        # Deshabilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.DISABLED)

    def confirmar_actualizacion(self):
        """Confirma la actualización del cliente"""
        # Validar campos vacíos
        campos_vacios = []
        for nombre, campo in self.campos.items():
            if not campo.get().strip():
                campos_vacios.append(nombre.replace("numTelC", "Teléfono")
                                     .replace("nombreC", "Nombre")
                                     .replace("correo", "Correo")
                                     .replace("clave", "Clave"))

        if campos_vacios:
            messagebox.showwarning("Campos vacíos",
                                   f"Los siguientes campos están vacíos:\n{', '.join(campos_vacios)}")
            return

        datos = {
            'telefono_original': self.telefono_original,
            'numTelC': self.campos['numTelC'].get(),
            'nombreC': self.campos['nombreC'].get(),
            'correo': self.campos['correo'].get(),
            'clave': self.campos['clave'].get()
        }

        try:
            # Primero verificar si el nuevo teléfono ya existe (si cambió)
            if datos['numTelC'] != datos['telefono_original']:
                self.cursor.execute("SELECT COUNT(*) FROM cliente WHERE numTelC = %s", (datos['numTelC'],))
                if self.cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "El nuevo número de teléfono ya existe")
                    return

            # Actualizar el cliente
            self.cursor.execute("""
                UPDATE cliente 
                SET numTelC = %s, nombreC = %s, correo = %s, clave = %s
                WHERE numTelC = %s
            """, (datos['numTelC'], datos['nombreC'], datos['correo'], datos['clave'], datos['telefono_original']))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            self.cancelar_edicion()
            self.volver_a_lista()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente: {str(e)}")

    def cancelar_edicion(self):
        """Cancela el modo de edición"""
        self.limpiar_campos()
        self.modo_edicion = False
        self.telefono_original = None

        # Ocultar botones secundarios
        self.frame_botones_secundarios.grid_remove()

        # Habilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.NORMAL)

    def volver_a_lista(self):
        """Vuelve a mostrar la lista de nombres"""
        self.mostrar_nombres()
        self.cliente_seleccionado = None
        self.frame_botones_secundarios.grid_remove()

        # Habilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.NORMAL)

    def crear_cliente(self):
        """Crea un nuevo cliente"""
        datos = self.obtener_datos()

        # Validar campos vacíos
        campos_vacios = []
        for nombre, campo in self.campos.items():
            if not campo.get().strip():
                campos_vacios.append(nombre.replace("numTelC", "Teléfono")
                                     .replace("nombreC", "Nombre")
                                     .replace("correo", "Correo")
                                     .replace("clave", "Clave"))

        if campos_vacios:
            messagebox.showwarning("Campos vacíos",
                                   f"Los siguientes campos están vacíos:\n{', '.join(campos_vacios)}")
            return

        try:
            self.cursor.execute("""
                INSERT INTO cliente (numTelC, nombreC, correo, clave)
                VALUES (%s, %s, %s, %s)
            """, (datos['numTelC'], datos['nombreC'], datos['correo'], datos['clave']))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Cliente creado correctamente")
            self.volver_a_lista()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el cliente: {str(e)}")

    def borrar_cliente(self):
        """Borra un cliente existente"""
        if not self.cliente_seleccionado:
            messagebox.showwarning("Advertencia", "Primero use 'Leer' en un cliente")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de borrar este cliente?"):
            try:
                self.cursor.execute("DELETE FROM cliente WHERE numTelC = %s", (self.cliente_seleccionado[0],))
                self.conexion.commit()
                messagebox.showinfo("Éxito", "Cliente borrado correctamente")
                self.volver_a_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar el cliente: {str(e)}")

    def obtener_datos(self):
        """Obtiene los datos de los campos de entrada"""
        return {
            'numTelC': self.campos['numTelC'].get(),
            'nombreC': self.campos['nombreC'].get(),
            'correo': self.campos['correo'].get(),
            'clave': self.campos['clave'].get()
        }

    def limpiar_campos(self):
        """Limpia todos los campos de entrada"""
        for campo in self.campos.values():
            campo.delete(0, tk.END)

    def __del__(self):
        """Cierra la conexión a la base de datos al salir"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conexion'):
            self.conexion.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientesApp(root)
    root.mainloop()