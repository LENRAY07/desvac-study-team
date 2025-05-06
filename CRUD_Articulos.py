import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime


class ArticulosApp:
    def __init__(self, parent, main_root):
        self.parent = parent
        self.main_root = main_root
        self.root = parent
        self.root.configure(bg="#5bfcfe")

        # Variables de estado
        self.modo_edicion = False
        self.articulo_seleccionado = None
        self.codigo_original = None

        # Conexión a MySQL
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="dbtiendaletty"
        )
        self.cursor = self.conexion.cursor()

        self.crear_interfaz()
        self.crear_tabla_articulos()
        self.crear_tabla_detalles()
        self.mostrar_articulos()

    def crear_tabla_articulos(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS articulos (
                    codigoBarras CHAR(13) PRIMARY KEY,
                    nombreArt VARCHAR(80),
                    marca VARCHAR(50),
                    cantidadAlmacen INT DEFAULT 0,
                    precioUnit DECIMAL(10,2) DEFAULT 0,
                    caducidad DATE NULL
                )
            """)
            self.conexion.commit()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la tabla articulos: {str(e)}")

    def crear_tabla_detalles(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS detalles (
                    claveProv CHAR(12) NOT NULL,
                    codigoBarras CHAR(13) NOT NULL,
                    costos DECIMAL(10,2) DEFAULT 0,
                    cantidadCompra INT DEFAULT 0,
                    PRIMARY KEY (claveProv, codigoBarras),
                    FOREIGN KEY (claveProv) REFERENCES proveedores(claveProv),
                    FOREIGN KEY (codigoBarras) REFERENCES articulos(codigoBarras)
                )
            """)
            self.conexion.commit()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la tabla detalles: {str(e)}")

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
        tk.Label(self.root, text="Artículos", font=("Impact", 20, "bold"), bg="#5bfcfe"
                 ).grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

        # Campos de entrada
        self.campos = {}
        campos_config = [
            ("Código Barras (13 dígitos):", "codigoBarras", ""),
            ("Nombre:", "nombreArt", ""),
            ("Marca:", "marca", ""),
            ("Cantidad en almacén:", "cantidadAlmacen", ""),
            ("Precio unitario:", "precioUnit", ""),
            ("Caducidad (AAAA-MM-DD):", "caducidad", ""),
            ("Clave de proveedor:", "claveProv", "")
        ]

        for i, (texto, nombre, _) in enumerate(campos_config, start=1):
            tk.Label(self.root, text=texto, font=("Arial", 12), bg="#5bfcfe"
                     ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entry = tk.Entry(self.root, font=("Arial", 12), bg="#e6ffff")
            entry.grid(row=i, column=2, padx=10, pady=5, sticky="ew")
            self.campos[nombre] = entry

        # Frame para botones principales
        frame_botones = tk.Frame(self.root, bg="#5bfcfe")
        frame_botones.grid(row=9, column=0, columnspan=3, pady=10)

        # Botones CRUD
        botones = [
            ("Añadir", "#A2E4B8", self.crear_articulo),
            ("Editar", "#FFE08A", self.editar_articulo),
            ("Borrar", "#F4A4A4", self.borrar_articulo)
        ]

        for i, (texto, color, comando) in enumerate(botones):
            tk.Button(frame_botones, text=texto, bg=color, font=("Arial", 10),
                      command=comando).grid(row=0, column=i, padx=5, ipadx=5, ipady=3)

        # Treeview
        frame_tabla = tk.Frame(self.root)
        frame_tabla.grid(row=10, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))

        columnas = [
            ("Código", 120),
            ("Nombre", 200),
            ("Marca", 100),
            ("Cantidad", 80),
            ("Precio", 80),
            ("Caducidad", 100),
            ("Proveedor", 100)
        ]

        self.tabla = ttk.Treeview(frame_tabla, columns=[col[0] for col in columnas],
                                  show="headings", height=12)

        for col, width in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_articulo)

    def mostrar_articulos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            self.cursor.execute("""
                SELECT a.codigoBarras, a.nombreArt, a.marca, a.cantidadAlmacen, 
                       a.precioUnit, a.caducidad, d.claveProv
                FROM articulos a
                LEFT JOIN detalles d ON a.codigoBarras = d.codigoBarras
                ORDER BY a.nombreArt
            """)

            for articulo in self.cursor.fetchall():
                caducidad = articulo[5].strftime("%Y-%m-%d") if articulo[5] else ""
                self.tabla.insert("", "end", values=(
                    articulo[0], articulo[1], articulo[2], articulo[3],
                    f"${articulo[4]:.2f}", caducidad, articulo[6] or ""
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar artículos: {str(e)}")

    def obtener_datos(self):
        return {clave: entry.get().strip() for clave, entry in self.campos.items()}

    def validar_datos(self, datos):
        if not datos['codigoBarras'] or not datos['nombreArt']:
            messagebox.showwarning("Error", "Código y nombre son obligatorios")
            return False

        if len(datos['codigoBarras']) != 13 or not datos['codigoBarras'].isdigit():
            messagebox.showerror("Error", "Código debe tener 13 dígitos")
            return False

        try:
            datos['cantidadAlmacen'] = int(datos['cantidadAlmacen']) if datos['cantidadAlmacen'] else 0
            datos['precioUnit'] = float(datos['precioUnit']) if datos['precioUnit'] else 0.0

            if datos['caducidad']:
                datetime.strptime(datos['caducidad'], "%Y-%m-%d")

            return True
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
            return False

    def crear_articulo(self):
        datos = self.obtener_datos()

        if not self.validar_datos(datos):
            return

        try:
            self.cursor.execute("START TRANSACTION")

            # Insertar artículo
            self.cursor.execute("""
                INSERT INTO articulos (codigoBarras, nombreArt, marca, 
                                      cantidadAlmacen, precioUnit, caducidad)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                datos['codigoBarras'],
                datos['nombreArt'],
                datos['marca'],
                datos['cantidadAlmacen'],
                datos['precioUnit'],
                datos['caducidad'] if datos['caducidad'] else None
            ))

            # Insertar relación con proveedor si existe
            if datos['claveProv']:
                self.cursor.execute("""
                    INSERT INTO detalles (claveProv, codigoBarras)
                    VALUES (%s, %s)
                """, (datos['claveProv'], datos['codigoBarras']))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Artículo creado correctamente")
            self.mostrar_articulos()
            self.limpiar_campos()

        except mysql.connector.IntegrityError as e:
            self.conexion.rollback()
            if "Duplicate entry" in str(e):
                messagebox.showerror("Error", "El código de barras ya existe")
            elif "foreign key constraint fails" in str(e):
                messagebox.showerror("Error", "La clave de proveedor no existe")
            else:
                messagebox.showerror("Error", f"Error de integridad: {str(e)}")
        except Exception as e:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo crear el artículo: {str(e)}")

    def editar_articulo(self):
        if not self.articulo_seleccionado:
            messagebox.showerror("Error", "Seleccione un artículo primero")
            return

        datos = self.obtener_datos()

        if not self.validar_datos(datos):
            return

        try:
            self.cursor.execute("START TRANSACTION")

            # Actualizar artículo
            self.cursor.execute("""
                UPDATE articulos SET
                    codigoBarras = %s,
                    nombreArt = %s,
                    marca = %s,
                    cantidadAlmacen = %s,
                    precioUnit = %s,
                    caducidad = %s
                WHERE codigoBarras = %s
            """, (
                datos['codigoBarras'],
                datos['nombreArt'],
                datos['marca'],
                datos['cantidadAlmacen'],
                datos['precioUnit'],
                datos['caducidad'] if datos['caducidad'] else None,
                self.codigo_original
            ))

            # Actualizar relación con proveedor
            if datos['claveProv']:
                # Primero verificar si ya existe una relación
                self.cursor.execute("""
                    SELECT 1 FROM detalles 
                    WHERE codigoBarras = %s
                """, (self.codigo_original,))

                if self.cursor.fetchone():
                    # Actualizar relación existente
                    self.cursor.execute("""
                        UPDATE detalles SET
                            claveProv = %s
                        WHERE codigoBarras = %s
                    """, (datos['claveProv'], self.codigo_original))
                else:
                    # Crear nueva relación
                    self.cursor.execute("""
                        INSERT INTO detalles (claveProv, codigoBarras)
                        VALUES (%s, %s)
                    """, (datos['claveProv'], self.codigo_original))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
            self.mostrar_articulos()
            self.limpiar_campos()
            self.articulo_seleccionado = None

        except mysql.connector.IntegrityError as e:
            self.conexion.rollback()
            if "Duplicate entry" in str(e):
                messagebox.showerror("Error", "El código de barras ya existe")
            elif "foreign key constraint fails" in str(e):
                messagebox.showerror("Error", "La clave de proveedor no existe")
            else:
                messagebox.showerror("Error", f"Error de integridad: {str(e)}")
        except Exception as e:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")

    def borrar_articulo(self):
        if not self.articulo_seleccionado:
            messagebox.showerror("Error", "Seleccione un artículo primero")
            return

        if not messagebox.askyesno("Confirmar", "¿Borrar este artículo y sus relaciones?"):
            return

        try:
            self.cursor.execute("START TRANSACTION")
            codigo = self.articulo_seleccionado[0]

            # Borrar primero las relaciones
            self.cursor.execute("""
                DELETE FROM detalles 
                WHERE codigoBarras = %s
            """, (codigo,))

            # Luego borrar el artículo
            self.cursor.execute("""
                DELETE FROM articulos 
                WHERE codigoBarras = %s
            """, (codigo,))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Artículo borrado correctamente")
            self.mostrar_articulos()
            self.limpiar_campos()
            self.articulo_seleccionado = None

        except Exception as e:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo borrar: {str(e)}")

    def seleccionar_articulo(self, event):
        seleccion = self.tabla.focus()
        if seleccion:
            valores = self.tabla.item(seleccion, "values")
            self.articulo_seleccionado = valores
            self.codigo_original = valores[0]  # Guardar código original para edición

            # Mapear valores a campos
            mapeo = {
                'codigoBarras': 0,
                'nombreArt': 1,
                'marca': 2,
                'cantidadAlmacen': 3,
                'precioUnit': 4,
                'caducidad': 5,
                'claveProv': 6
            }

            for campo, idx in mapeo.items():
                self.campos[campo].delete(0, tk.END)
                if idx < len(valores):
                    # Quitar el símbolo $ del precio si existe
                    valor = valores[idx].replace("$", "") if idx == 4 else valores[idx]
                    self.campos[campo].insert(0, valor)

    def limpiar_campos(self):
        for campo in self.campos.values():
            campo.delete(0, tk.END)

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conexion'):
            self.conexion.close()


