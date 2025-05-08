import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errorcode


class ProveedoresApp:
    def __init__(self, parent, main_root):
        self.parent = parent
        self.main_root = main_root
        self.root = parent
        self.root.configure(bg="#f0f2f5")  # Fondo más claro y moderno

        # Configuración de estilo general
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configurar estilos para los widgets
        self.style.configure('TFrame', background="#f0f2f5")
        self.style.configure('TLabel', background="#f0f2f5", font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), relief="flat")
        self.style.map('TButton',
                       background=[('active', '#e1e5ea')],
                       foreground=[('active', 'black')])

        self.style.configure('Treeview', font=('Segoe UI', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        self.style.map('Treeview', background=[('selected', '#4a98db')])

        # Variables de estado
        self.proveedor_seleccionado = None
        self.clave_original = None

        # Conexión a MySQL
        self.conectar_db()

        # Configuración de la interfaz
        self.crear_interfaz()
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

    def crear_interfaz(self):
        self.root.grid_columnconfigure(1, weight=1)
        for i in range(7):
            self.root.grid_rowconfigure(i, weight=0)

        # Título con estilo moderno
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        title_frame.grid_columnconfigure(0, weight=1)

        tk.Label(title_frame, text="Proveedores", font=("Segoe UI", 24, "bold"),
                 bg="#2c3e50", fg="white").grid(row=0, column=0, pady=20)

        # Frame principal para los campos
        form_frame = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=10)
        form_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.campos = {}
        etiquetas = [
            ("Clave:", "claveProv"),
            ("Teléfono:", "numTelProv"),
            ("Empresa:", "empresa"),
            ("Costos:", "costos"),
            ("Cantidad comprada:", "cantidadEntregada")
        ]

        for i, (texto, clave) in enumerate(etiquetas, 0):
            tk.Label(form_frame, text=texto, font=("Segoe UI", 11),
                     bg="#f0f2f5", fg="#2c3e50").grid(row=i, column=0, padx=10, pady=8, sticky="w")
            entrada = tk.Entry(form_frame, font=("Segoe UI", 11),
                               bg="white", bd=2, relief="groove", highlightthickness=0)
            entrada.grid(row=i, column=1, padx=10, pady=8, sticky="ew")
            self.campos[clave] = entrada

        # Frame para botones principales
        button_frame = tk.Frame(self.root, bg="#f0f2f5", pady=15)
        button_frame.grid(row=2, column=0, columnspan=3, sticky="ew")

        botones = [
            ("Añadir", "#27ae60", self.crear_proveedor),
            ("Editar", "#f39c12", self.editar_proveedor),
            ("Borrar", "#e74c3c", self.borrar_proveedor),
            ("Limpiar", "#95a5a6", self.limpiar_campos)
        ]

        for idx, (texto, color, comando) in enumerate(botones):
            btn = tk.Button(button_frame, text=texto, command=comando,
                            bg=color, fg="white", font=("Segoe UI", 10, "bold"),
                            activebackground=color, activeforeground="white",
                            relief="flat", bd=0, padx=15, pady=8)
            btn.grid(row=0, column=idx, padx=10, ipadx=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.lighten_color(b.cget("bg"))))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

        # Frame para la tabla
        table_frame = tk.Frame(self.root, bg="#f0f2f5")
        table_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columnas = ["Clave", "Teléfono", "Empresa", "Costos", "Cantidad"]
        self.tabla = ttk.Treeview(table_frame, columns=columnas,
                                  show="headings", height=12, style="Treeview")

        column_widths = {"Clave": 90, "Teléfono": 100, "Empresa": 150, "Costos": 100, "Cantidad": 120}
        for col in columnas:
            anchor = "center" if col in ["Costos", "Cantidad"] else "w"
            self.tabla.heading(col, text=col, anchor=anchor)
            self.tabla.column(col, width=column_widths.get(col, 100), anchor=anchor)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_proveedor)

    def lighten_color(self, color, amount=0.2):
        """Aclara un color hexadecimal"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        lighter = tuple(min(255, int(c + (255 - c) * amount)) for c in rgb)
        return f'#{lighter[0]:02x}{lighter[1]:02x}{lighter[2]:02x}'

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

            # Cargar datos en los campos SIN llamar a limpiar_campos antes para evitar borrar el insertado
            for campo, valor in zip(self.campos.keys(), item['values']):
                cleaned_val = valor
                if campo == 'costos' and isinstance(valor, str):
                    cleaned_val = valor.replace('$', '').replace(',', '')
                self.campos[campo].delete(0, tk.END)
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

            # Verificar si los datos han cambiado; si no, no actualizar
            self.cursor.execute("""
                SELECT numTelProv, empresa, 
                       (SELECT costos FROM detalles WHERE claveProv = %s) AS costos,
                       (SELECT cantidadEntregada FROM detalles WHERE claveProv = %s) AS cantidadEntregada
                FROM proveedores WHERE claveProv = %s
            """, (self.clave_original, self.clave_original, self.clave_original))
            proveedor_actual = self.cursor.fetchone()

            # Comparar los datos actuales con los nuevos
            if (datos['numTelProv'] == proveedor_actual['numTelProv'] and
                    datos['empresa'] == proveedor_actual['empresa'] and
                    costos == float(proveedor_actual['costos']) and
                    cantidad == proveedor_actual['cantidadEntregada'] and
                    datos['claveProv'] == self.clave_original):
                messagebox.showinfo("Sin cambios", "No se realizaron cambios en los datos del proveedor.")
                return

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

