import tkinter as tk
from logging import exception
from tkinter import ttk, messagebox
import mysql.connector


class ClientesApp:
    def __init__(self, parent, main_root):
        self.parent = parent
        self.main_root = main_root
        self.root = parent
        #self.root.title("Clientes")
        #self.root.geometry("1000x600")
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
                    correo VARCHAR(50)
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
        for i in range(10):
            self.root.grid_rowconfigure(i, weight=0)
        self.root.grid_rowconfigure(10, weight=1)

        # Título
        tk.Label(self.root, text="Clientes", font=("Impact", 20, "bold"), bg="#5bfcfe"
                 ).grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

        # Campos de entrada
        self.campos = {}
        campos_config = [
            ("Teléfono:", "numTelC", ""),
            ("Nombre:", "nombreC", ""),
            ("Correo:", "correo", ""),
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
            ("Añadir", "#A2E4B8", self.crear_cliente),
            ("Editar", "#FFE08A", self.editar_cliente),
            ("Borrar", "#F4A4A4", self.borrar_cliente)
        ]

        for i, (texto, color, comando) in enumerate(self.botones_principales):
            btn = tk.Button(frame_botones, text=texto, bg=color, font=("Arial", 12), command=comando)
            btn.grid(row=0, column=i, padx=5, ipadx=5, ipady=3)
            setattr(self, f"btn_{texto.lower()}", btn)

        # Frame para la tabla de clientes
        frame_tabla = tk.Frame(self.root)
        frame_tabla.grid(row=10, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))

        # Treeview para mostrar clientes
        self.tabla = ttk.Treeview(frame_tabla, columns=("Telefono", "Nombre", "Correo",), show="headings")
        self.tabla.heading("Telefono", text="Telefono")
        self.tabla.column("Telefono", width=100)
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.column("Nombre", width=300)
        self.tabla.heading("Correo", text="Correo")
        self.tabla.column("Correo", width=100)

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_cliente)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Posicionamiento
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mostrar_nombres(self):
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            self.cursor.execute("SELECT numTelC, nombreC, correo FROM cliente ORDER BY nombreC")
            nombres = self.cursor.fetchall()

            for nombre in nombres:
                self.tabla.insert("", "end", values=nombre)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los nombres: {str(e)}")

    def obtener_datos(self):
        return{clave: entry.get().strip() for clave, entry in self.campos.items()}

    def crear_cliente(self):
        """Crea un nuevo cliente"""
        datos = self.obtener_datos()

        # Validar campos vacíos
        campos_vacios = []
        for nombre, campo in self.campos.items():
            if not campo.get().strip():
                campos_vacios.append(nombre.replace("numTelC", "Teléfono")
                                     .replace("nombreC", "Nombre")
                                     .replace("correo", "Correo"))

        if campos_vacios:
            messagebox.showwarning("Campos vacíos",
                                   f"Los siguientes campos están vacíos:\n{', '.join(campos_vacios)}")
            return

        try:
            self.cursor.execute("""
                INSERT INTO cliente (numTelC, nombreC, correo)
                VALUES (%s, %s, %s, %s)
            """, (datos['numTelC'], datos['nombreC'], datos['correo']))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Cliente creado correctamente")
            self.mostrar_nombres()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el cliente: {str(e)}")

    def limpiar_campos(self):
        """Limpia todos los campos de entrada"""
        for campo in self.campos.values():
            campo.delete(0, tk.END)

    def seleccionar_cliente(self, event=None):
        """Maneja la selección de un cliente en la tabla"""
        seleccion = self.tabla.selection()
        if seleccion:
            item = self.tabla.item(seleccion[0])
            self.cliente_seleccionado = item['values']  # Guarda todos los valores
            self.codigo_original = item['values'][0]  # Guarda el teléfono original

            # Llena los campos con los datos
            self.limpiar_campos()
            self.campos['numTelC'].insert(0, item['values'][0])
            self.campos['nombreC'].insert(0, item['values'][1])
            self.campos['correo'].insert(0, item['values'][2])

    def editar_cliente(self):
        """Edita un cliente existente"""
        if not hasattr(self, 'cliente_seleccionado') or not self.cliente_seleccionado:
            messagebox.showerror("Error", "Seleccione un cliente primero")
            return

        datos = self.obtener_datos()

        # Validación de campos
        campos_requeridos = {
            'numTelC': 'Teléfono',
            'nombreC': 'Nombre',
        }

        campos_vacios = []
        for campo, nombre in campos_requeridos.items():
            if not datos.get(campo, '').strip():
                campos_vacios.append(nombre)

        if campos_vacios:
            messagebox.showwarning("Campos requeridos",
                                   f"Debe completar: {', '.join(campos_vacios)}")
            return

        try:
            # Verificar si el teléfono ya existe (solo si cambió)
            if datos['numTelC'] != self.codigo_original:
                self.cursor.execute("SELECT numTelC FROM cliente WHERE numTelC = %s", (datos['numTelC'],))
                if self.cursor.fetchone():
                    messagebox.showerror("Error", "El teléfono ya está registrado")
                    return

            # Actualizar el cliente
            self.cursor.execute("""
                UPDATE cliente 
                SET numTelC = %s, 
                    nombreC = %s, 
                    correo = %s 
                WHERE numTelC = %s
            """, (
                datos['numTelC'],
                datos['nombreC'],
                datos['correo'],
                self.codigo_original
            ))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            self.mostrar_nombres()
            self.limpiar_campos()
            self.cliente_seleccionado = None
            self.codigo_original = None

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente: {str(e)}")


    def borrar_cliente(self):
        if not self.cliente_seleccionado:
            messagebox.showerror("Error", "No se ha seleccionado un cliente para borrar")
            return
        confirmacion= messagebox.askyesno("Confirmar", "¿Seguro que deseas borrar al cliente?")
        if not confirmacion:
            return

        try:
            codigo = self.cliente_seleccionado[0]
            self.cursor.execute("DELETE FROM cliente WHERE numTelC =%s", (codigo,))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Cliente borrado correctamente")
            self.mostrar_nombres()
            self.cliente_seleccionado = None
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo borrar al cliente: {str(e)}")
            self.limpiar_campos()

    def __del__(self):
        """Cierra la conexión a la base de datos al salir"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conexion'):
            self.conexion.close()

