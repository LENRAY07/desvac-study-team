import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errorcode


class ProveedoresApp:
    def __init__(self, parent, main_root):
        self.parent = parent
        self.main_root = main_root
        self.root = parent
        self.root.configure(bg="#5bfcfe")

        # Variables de estado
        self.proveedor_seleccionado = None
        self.clave_original = None

        # Conexión a MySQL
        self.conectar_db()

        # Configuración de la interfaz
        self.configurar_interfaz()
        self.crear_tablas()
        self.mostrar_proveedores()

    def conectar_db(self):
        """Establece la conexión con la base de datos"""
        try:
            self.conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysql",
                database="dbtiendaletty"
            )
            self.cursor = self.conexion.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al conectar a la base de datos: {err}")
            raise

    def configurar_interfaz(self):
        """Configura los elementos de la interfaz gráfica"""
        # Configuración del grid
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1 if i > 0 else 0)
        for i in range(7):
            self.root.grid_rowconfigure(i, weight=1 if i == 6 else 0)

        # Título
        tk.Label(self.root, text="Proveedores", font=("Impact", 20, "bold"),
                 bg="#5bfcfe").grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

        # Campos de entrada
        self.campos = {}
        campos_config = [
            ("Clave:", "claveProv", "", 12),
            ("Teléfono:", "numTelProv", "", 10),
            ("Empresa:", "empresa", "", 30),
            ("Costos:", "costos", "", 10),
            ("Cantidad comprada:", "cantidadEntregada", "", 10)
        ]

        for i, (texto, nombre, show_char, maxlength) in enumerate(campos_config, 1):
            tk.Label(self.root, text=texto, font=("Arial", 14), bg="#5bfcfe"
                     ).grid(row=i, column=0, padx=10, pady=10, sticky="w")

            entry = tk.Entry(self.root, font=("Arial", 14), bg="#e6ffff",
                             show=show_char, validate="key")
            if maxlength:
                entry['validatecommand'] = (entry.register(self.validar_longitud), '%P', maxlength)
            entry.grid(row=i, column=2, padx=(0, 20), pady=10, sticky="ew")
            self.campos[nombre] = entry

        # Botones principales
        self.crear_botones()

        # Tabla de proveedores
        self.configurar_tabla()

    def validar_longitud(self, texto, maxlength):
        """Valida que el texto no exceda la longitud máxima"""
        return len(texto) <= int(maxlength)

    def crear_botones(self):
        """Crea los botones de la interfaz"""
        frame_botones = tk.Frame(self.root, bg="#5bfcfe")
        frame_botones.grid(row=7, column=0, columnspan=3, pady=20)

        botones = [
            ("Añadir", "#A2E4B8", self.crear_proveedor),
            ("Editar", "#FFE08A", self.editar_proveedor),
            ("Borrar", "#F4A4A4", self.borrar_proveedor),
            ("Limpiar", "#D3D3D3", self.limpiar_campos)
        ]

        for i, (texto, color, comando) in enumerate(botones):
            tk.Button(frame_botones, text=texto, bg=color, font=("Arial", 12),
                      command=comando).grid(row=0, column=i, padx=10, ipadx=10, ipady=5)

    def configurar_tabla(self):
        """Configura la tabla de proveedores"""
        frame_tabla = tk.Frame(self.root)
        frame_tabla.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))

        columnas = [
            ("Clave", 90),
            ("Teléfono", 100),
            ("Empresa", 150),
            ("Costos", 100),
            ("Cantidad", 120)
        ]

        self.tabla = ttk.Treeview(frame_tabla, columns=[col[0] for col in columnas],
                                  show="headings", height=12)

        for col, width in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=width, anchor=tk.CENTER if col in ["Costos", "Cantidad"] else tk.W)

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_proveedor)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def crear_tablas(self):
        """Crea las tablas necesarias en la base de datos"""
        tablas = {
            "proveedores": """
                CREATE TABLE IF NOT EXISTS proveedores (
                    claveProv CHAR(12) PRIMARY KEY,
                    numTelProv CHAR(10),
                    empresa VARCHAR(30)
                )
            """,
            "detalles": """
                CREATE TABLE IF NOT EXISTS detalles (
                    claveProv CHAR(12) PRIMARY KEY,
                    costos DECIMAL(10,2) DEFAULT 0,
                    cantidadEntregada INT DEFAULT 0,
                    FOREIGN KEY (claveProv) REFERENCES proveedores(claveProv)
                )
            """
        }

        for nombre, sql in tablas.items():
            try:
                self.cursor.execute(sql)
                self.conexion.commit()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo crear la tabla {nombre}: {err}")

    def mostrar_proveedores(self):
        """Muestra todos los proveedores en la tabla"""
        self.tabla.delete(*self.tabla.get_children())

        try:
            self.cursor.execute("""
                SELECT p.claveProv, p.numTelProv, p.empresa, 
                       COALESCE(d.costos, 0) as costos, 
                       COALESCE(d.cantidadEntregada, 0) as cantidadEntregada
                FROM proveedores p
                LEFT JOIN detalles d ON p.claveProv = d.claveProv
                ORDER BY p.empresa
            """)

            for proveedor in self.cursor.fetchall():
                self.tabla.insert("", "end", values=(
                    proveedor['claveProv'],
                    proveedor['numTelProv'],
                    proveedor['empresa'],
                    f"${proveedor['costos']:.2f}",
                    proveedor['cantidadEntregada']
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudieron cargar los proveedores: {err}")

    def obtener_datos(self):
        """Obtiene los datos de los campos de entrada"""
        return {clave: entry.get().strip() for clave, entry in self.campos.items()}

    def validar_datos(self, datos, edicion=False):
        """Valida los datos del formulario"""
        errores = []

        # Validar campos obligatorios
        if not datos['claveProv']:
            errores.append("La clave es obligatoria")
        if not datos['empresa']:
            errores.append("La empresa es obligatoria")

        # Validar formatos
        if datos['numTelProv'] and (not datos['numTelProv'].isdigit() or len(datos['numTelProv']) != 10):
            errores.append("Teléfono debe tener 10 dígitos")

        try:
            float(datos['costos'] or 0)
        except ValueError:
            errores.append("Costos debe ser un número")

        try:
            int(datos['cantidadEntregada'] or 0)
        except ValueError:
            errores.append("Cantidad debe ser un número entero")

        return errores

    def crear_proveedor(self):
        """Crea un nuevo proveedor"""
        datos = self.obtener_datos()
        errores = self.validar_datos(datos)

        if errores:
            messagebox.showwarning("Validación", "\n".join(errores))
            return

        try:
            costos = float(datos['costos'] or 0)
            cantidad = int(datos['cantidadEntregada'] or 0)

            self.cursor.execute("START TRANSACTION")

            # Insertar proveedor
            self.cursor.execute("""
                INSERT INTO proveedores (claveProv, numTelProv, empresa)
                VALUES (%s, %s, %s)
            """, (datos['claveProv'], datos['numTelProv'] or None, datos['empresa']))

            # Insertar detalles
            self.cursor.execute("""
                INSERT INTO detalles (claveProv, costos, cantidadEntregada)
                VALUES (%s, %s, %s)
            """, (datos['claveProv'], costos, cantidad))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Proveedor creado correctamente")
            self.mostrar_proveedores()
            self.limpiar_campos()

        except mysql.connector.IntegrityError as err:
            self.conexion.rollback()
            if err.errno == errorcode.ER_DUP_ENTRY:
                messagebox.showerror("Error", "La clave ya existe")
            else:
                messagebox.showerror("Error", f"Error de integridad: {err}")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo crear el proveedor: {err}")

    def seleccionar_proveedor(self, event):
        """Selecciona un proveedor de la tabla"""
        seleccion = self.tabla.focus()
        if seleccion:
            item = self.tabla.item(seleccion)
            self.proveedor_seleccionado = item['values']
            self.clave_original = item['values'][0]

            # Limpiar y cargar datos en los campos
            self.limpiar_campos()
            for campo, valor in zip(self.campos.keys(), item['values']):
                # Eliminar formato de dinero si es necesario
                cleaned_val = valor.replace('$', '') if campo == 'costos' else valor
                self.campos[campo].insert(0, cleaned_val)

    def editar_proveedor(self):
        """Edita un proveedor existente"""
        if not self.proveedor_seleccionado:
            messagebox.showwarning("Error", "Seleccione un proveedor para editar")
            return

        datos = self.obtener_datos()
        errores = self.validar_datos(datos, edicion=True)

        if errores:
            messagebox.showwarning("Validación", "\n".join(errores))
            return

        try:
            costos = float(datos['costos'] or 0)
            cantidad = int(datos['cantidadEntregada'] or 0)

            self.cursor.execute("START TRANSACTION")

            # Actualizar proveedor
            self.cursor.execute("""
                UPDATE proveedores 
                SET numTelProv = %s, 
                    empresa = %s 
                WHERE claveProv = %s
            """, (datos['numTelProv'] or None, datos['empresa'], self.clave_original))

            # Actualizar detalles
            self.cursor.execute("""
                UPDATE detalles
                SET costos = %s,
                    cantidadEntregada = %s
                WHERE claveProv = %s
            """, (costos, cantidad, self.clave_original))

            # Si cambió la clave, actualizarla en ambas tablas
            if datos['claveProv'] != self.clave_original:
                self.cursor.execute("""
                    UPDATE proveedores
                    SET claveProv = %s
                    WHERE claveProv = %s
                """, (datos['claveProv'], self.clave_original))

                self.cursor.execute("""
                    UPDATE detalles
                    SET claveProv = %s
                    WHERE claveProv = %s
                """, (datos['claveProv'], self.clave_original))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Proveedor actualizado correctamente")
            self.mostrar_proveedores()
            self.limpiar_campos()
            self.proveedor_seleccionado = None

        except mysql.connector.IntegrityError as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"Error de integridad: {err}")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"Error al actualizar: {err}")

    def borrar_proveedor(self):
        """Elimina un proveedor"""
        if not self.proveedor_seleccionado:
            messagebox.showwarning("Error", "Seleccione un proveedor para borrar")
            return

        if not messagebox.askyesno("Confirmar", "¿Borrar este proveedor y sus detalles?"):
            return

        try:
            self.cursor.execute("START TRANSACTION")

            # Borrar detalles primero por la FK
            self.cursor.execute("DELETE FROM detalles WHERE claveProv = %s", (self.clave_original,))
            # Luego borrar proveedor
            self.cursor.execute("DELETE FROM proveedores WHERE claveProv = %s", (self.clave_original,))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Proveedor borrado correctamente")
            self.mostrar_proveedores()
            self.limpiar_campos()
            self.proveedor_seleccionado = None

        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo borrar: {err}")

    def limpiar_campos(self):
        """Limpia todos los campos de entrada"""
        for campo in self.campos.values():
            campo.delete(0, tk.END)
        self.proveedor_seleccionado = None

    def __del__(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conexion') and self.conexion.is_connected():
            self.conexion.close()
