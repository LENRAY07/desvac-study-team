import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime


class ArticulosApp:
    def __init__(self, parent, main_root):
        self.parent = parent
        self.main_root = main_root
        self.root = parent
        self.root.configure(bg="#f0f2f5")  # Fondo claro y moderno

        self.articulo_seleccionado = None
        self.codigo_original = None
        self.modo_edicion = False

        try:
            self.conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysql",
                database="dbtiendaletty"
            )
            self.cursor = self.conexion.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{err}")
            return

        self.crear_tablas()
        self.configurar_interfaz()
        self.mostrar_articulos()

    def configurar_interfaz(self):
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(8):
            self.root.grid_rowconfigure(i, weight=0)
        self.root.grid_rowconfigure(7, weight=1)

        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        title_frame.grid_columnconfigure(0, weight=1)

        tk.Label(title_frame, text="Artículos",
                 font=("Segoe UI", 24, "bold"), bg="#2c3e50", fg="white").grid(row=0, column=0, pady=20)

        form_frame = tk.Frame(self.root, bg="#f0f2f5")
        form_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20)
        form_frame.grid_columnconfigure(1, weight=1)

        self.campos = {}
        labels = [
            ("Código Barras (13 dígitos):", "codigoBarras"),
            ("Nombre:", "nombreArt"),
            ("Marca:", "marca"),
            ("Cantidad en almacén:", "cantidadAlmacen"),
            ("Precio unitario:", "precioUnit"),
            ("Caducidad (AAAA-MM-DD):", "caducidad"),
            ("Clave de proveedor:", "claveProv")
        ]
        maxlengths = {
            "codigoBarras": 13,
            "nombreArt": 80,
            "marca": 50,
            "cantidadAlmacen": 10,
            "precioUnit": 15,
            "caducidad": 10,
            "claveProv": 12
        }

        for idx, (text, key) in enumerate(labels):
            lbl = tk.Label(form_frame, text=text, font=("Segoe UI", 11), bg="#f0f2f5", anchor="w")
            lbl.grid(row=idx, column=0, sticky="w", pady=6, padx=(0, 10))
            entry = tk.Entry(form_frame, font=("Segoe UI", 11), bg="white", relief="groove", bd=2)
            entry.grid(row=idx, column=1, sticky="ew", pady=6)
            entry.configure(validate="key",
                            validatecommand=(entry.register(self.validar_longitud), '%P', maxlengths[key]))
            self.campos[key] = entry

        button_frame = tk.Frame(self.root, bg="#f0f2f5")
        button_frame.grid(row=2, column=0, columnspan=3, pady=15)

        botones = [
            ("Añadir", "#27ae60", self.crear_articulo),
            ("Editar", "#f39c12", self.editar_articulo),
            ("Borrar", "#e74c3c", self.borrar_articulo),
            ("Limpiar", "#95a5a6", self.limpiar_campos)
        ]

        for i, (text, color, cmd) in enumerate(botones):
            btn = tk.Button(button_frame, text=text, command=cmd, bg=color, fg="white",
                            font=("Segoe UI", 11, "bold"), relief="flat", bd=0, padx=15, pady=8,
                            activebackground=self.aclarar_color(color, 20), activeforeground="white")
            btn.grid(row=0, column=i, padx=10, ipadx=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.aclarar_color(b['bg'], 15)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

        table_frame = tk.Frame(self.root, bg="#f0f2f5")
        table_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"),
                        background="#34495e", foreground="white", padding=5)
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        style.map("Treeview", background=[("selected", "#3498db")])

        self.tabla = ttk.Treeview(table_frame,
                                  columns=("Código", "Nombre", "Marca", "Cantidad", "Precio", "Caducidad", "Proveedor"),
                                  show="headings", selectmode="browse")
        columnas = [
            ("Código", 130, "center"),
            ("Nombre", 200, "w"),
            ("Marca", 120, "center"),
            ("Cantidad", 80, "center"),
            ("Precio", 100, "center"),
            ("Caducidad", 100, "center"),
            ("Proveedor", 120, "center")
        ]
        for col, width, anchor in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=width, anchor=anchor)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_articulo)

    def aclarar_color(self, color_hex, amount=30):
        try:
            r = min(255, int(color_hex[1:3], 16) + amount)
            g = min(255, int(color_hex[3:5], 16) + amount)
            b = min(255, int(color_hex[5:7], 16) + amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color_hex

    def validar_longitud(self, texto, maxlength):
        return len(texto) <= int(maxlength)

    def crear_tablas(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS articulos (
                    codigoBarras CHAR(13) PRIMARY KEY,
                    nombreArt VARCHAR(80) NOT NULL,
                    marca VARCHAR(50),
                    cantidadAlmacen INT DEFAULT 0,
                    precioUnit DECIMAL(10,2) DEFAULT 0,
                    caducidad DATE NULL
                )
            """)
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
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudieron crear las tablas:\n{err}")

    def mostrar_articulos(self):
        self.tabla.delete(*self.tabla.get_children())
        try:
            self.cursor.execute("""
                SELECT a.codigoBarras, a.nombreArt, a.marca, a.cantidadAlmacen, 
                       a.precioUnit, a.caducidad, d.claveProv
                FROM articulos a
                LEFT JOIN detalles d ON a.codigoBarras = d.codigoBarras
                ORDER BY a.nombreArt
            """)
            for articulo in self.cursor.fetchall():
                caducidad = articulo['caducidad'].strftime("%Y-%m-%d") if articulo['caducidad'] else ""
                self.tabla.insert("", "end", values=(
                    articulo['codigoBarras'],
                    articulo['nombreArt'],
                    articulo['marca'],
                    articulo['cantidadAlmacen'],
                    f"${articulo['precioUnit']:.2f}",
                    caducidad,
                    articulo['claveProv'] or ""
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudieron cargar los artículos:\n{err}")

    def obtener_datos(self):
        return {k: v.get().strip() for k, v in self.campos.items()}

    def validar_datos(self, datos):
        errores = []
        if not datos['codigoBarras']:
            errores.append("El código de barras es obligatorio")
        elif len(datos['codigoBarras']) != 13 or not datos['codigoBarras'].isdigit():
            errores.append("El código de barras debe tener 13 dígitos")
        if not datos['nombreArt']:
            errores.append("El nombre es obligatorio")
        try:
            datos['cantidadAlmacen'] = int(datos['cantidadAlmacen'] or 0)
        except ValueError:
            errores.append("La cantidad debe ser un número entero")
        try:
            datos['precioUnit'] = float(datos['precioUnit'] or 0)
            if datos['precioUnit'] < 0:
                errores.append("El precio no puede ser negativo")
        except ValueError:
            errores.append("El precio debe ser un número válido")
        if datos['caducidad']:
            try:
                datetime.strptime(datos['caducidad'], "%Y-%m-%d")
            except ValueError:
                errores.append("Formato de fecha inválido (AAAA-MM-DD)")
        if errores:
            messagebox.showwarning("Validación", "\n".join(errores))
            return False
        return True

    def limpiar_campos(self):
        for campo in self.campos.values():
            campo.delete(0, tk.END)
        self.articulo_seleccionado = None
        self.codigo_original = None
        self.modo_edicion = False
        selection = self.tabla.selection()
        if selection:
            self.tabla.selection_remove(selection)

    def crear_articulo(self):
        datos = self.obtener_datos()
        if not self.validar_datos(datos):
            return
        try:
            self.cursor.execute("START TRANSACTION")
            self.cursor.execute("""
                INSERT INTO articulos (codigoBarras, nombreArt, marca, cantidadAlmacen, precioUnit, caducidad)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (datos['codigoBarras'], datos['nombreArt'], datos['marca'], datos['cantidadAlmacen'], datos['precioUnit'], datos['caducidad'] or None))
            if datos['claveProv']:
                self.cursor.execute("""
                    SELECT 1 FROM detalles WHERE claveProv = %s AND codigoBarras = %s
                """, (datos['claveProv'], datos['codigoBarras']))
                if not self.cursor.fetchone():
                    self.cursor.execute("""
                        INSERT INTO detalles (claveProv, codigoBarras)
                        VALUES (%s, %s)
                    """, (datos['claveProv'], datos['codigoBarras']))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Artículo creado correctamente")
            self.mostrar_articulos()
            self.limpiar_campos()
        except mysql.connector.IntegrityError as err:
            self.conexion.rollback()
            if err.errno == errorcode.ER_DUP_ENTRY:
                messagebox.showerror("Error", "El código de barras ya existe")
            elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                messagebox.showerror("Error", "La clave de proveedor no existe")
            else:
                messagebox.showerror("Error", f"Error de integridad:\n{err}")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo crear el artículo:\n{err}")

    def seleccionar_articulo(self, event):
        selected = self.tabla.selection()
        if selected:
            item_id = selected[0]
            item = self.tabla.item(item_id)
            self.articulo_seleccionado = item['values']
            self.codigo_original = item['values'][0]
            self.modo_edicion = True

            for campo in self.campos.values():
                campo.delete(0, tk.END)

            self.campos['codigoBarras'].insert(0, item['values'][0])
            self.campos['nombreArt'].insert(0, item['values'][1])
            self.campos['marca'].insert(0, item['values'][2])
            self.campos['cantidadAlmacen'].insert(0, item['values'][3])
            self.campos['precioUnit'].insert(0, item['values'][4].replace("$", ""))
            self.campos['caducidad'].insert(0, item['values'][5])
            self.campos['claveProv'].insert(0, item['values'][6])

    def editar_articulo(self):
        if not self.articulo_seleccionado:
            messagebox.showwarning("Error", "Seleccione un artículo para editar")
            return
        datos = self.obtener_datos()
        if not self.validar_datos(datos):
            return
        try:
            self.cursor.execute("START TRANSACTION")
            self.cursor.execute("""
                UPDATE articulos SET codigoBarras=%s, nombreArt=%s, marca=%s,
                cantidadAlmacen=%s, precioUnit=%s, caducidad=%s WHERE codigoBarras=%s
            """, (datos['codigoBarras'], datos['nombreArt'], datos['marca'], datos['cantidadAlmacen'],
                  datos['precioUnit'], datos['caducidad'] or None, self.codigo_original))
            if datos['claveProv']:
                self.cursor.execute("SELECT 1 FROM detalles WHERE codigoBarras = %s", (self.codigo_original,))
                if self.cursor.fetchone():
                    self.cursor.execute("UPDATE detalles SET claveProv = %s WHERE codigoBarras = %s",
                                        (datos['claveProv'], self.codigo_original))
                else:
                    self.cursor.execute("INSERT INTO detalles (claveProv, codigoBarras) VALUES (%s, %s)",
                                        (datos['claveProv'], self.codigo_original))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
            self.mostrar_articulos()
            self.limpiar_campos()
        except mysql.connector.IntegrityError as err:
            self.conexion.rollback()
            if err.errno == errorcode.ER_DUP_ENTRY:
                messagebox.showerror("Error", "El código de barras ya existe")
            elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                messagebox.showerror("Error", "La clave de proveedor no existe")
            else:
                messagebox.showerror("Error", f"Error de integridad:\n{err}")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo actualizar el artículo:\n{err}")

    def borrar_articulo(self):
        if not self.articulo_seleccionado:
            messagebox.showwarning("Error", "Seleccione un artículo para borrar")
            return

        confirmacion = messagebox.askyesno("Confirmar",
                                           f"¿Está seguro que desea eliminar el artículo:\n{self.articulo_seleccionado[1]}?")
        if not confirmacion:
            return

        try:
            self.cursor.execute("START TRANSACTION")

            # Primero, eliminamos el registro de la tabla detalles
            self.cursor.execute("DELETE FROM detalles WHERE codigoBarras = %s", (self.codigo_original,))

            # Luego, eliminamos el registro de la tabla articulos
            self.cursor.execute("DELETE FROM articulos WHERE codigoBarras = %s", (self.codigo_original,))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Artículo eliminado correctamente")
            self.mostrar_articulos()
            self.limpiar_campos()
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo eliminar el artículo:\n{err}")

    def limpiar_campos(self):
        for campo in self.campos.values():
            campo.delete(0, tk.END)
        self.articulo_seleccionado = None
        self.codigo_original = None
        self.modo_edicion = False
        selection = self.tabla.selection()
        if selection:
            self.tabla.selection_remove(selection)

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            try:
                self.cursor.close()
            except:
                pass
        if hasattr(self, 'conexion'):
            try:
                if self.conexion.is_connected():
                    self.conexion.close()
            except:
                pass

