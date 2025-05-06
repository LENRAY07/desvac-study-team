import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errorcode


class VentasApp:
    def __init__(self, parent, main_root):
        self.parent = parent
        self.main_root = main_root
        self.root = parent
        self.root.configure(bg="#5bfcfe")

        # Variables de estado
        self.modo_edicion = False
        self.venta_seleccionada = None

        # Conexión a MySQL
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="dbtiendaletty"
        )
        self.cursor = self.conexion.cursor()

        self.crear_interfaz()
        self.crear_tabla_ventas()
        self.mostrar_ventas()

    def crear_tabla_ventas(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                idVenta INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                numTelC CHAR(10) NULL,
                numTelV CHAR(10) NULL,
                totalpago DECIMAL(10,2) NULL,
                codigoBarras CHAR(13) NULL,
                FOREIGN KEY (numTelC) REFERENCES cliente(numTelC),
                FOREIGN KEY (numTelV) REFERENCES vendedor(numTelV),
                FOREIGN KEY (codigoBarras) REFERENCES articulos(codigoBarras))
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
        tk.Label(self.root, text="Ventas", font=("Impact", 20, "bold"), bg="#5bfcfe"
                 ).grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

        # Campos de entrada
        self.campos = {}
        campos_config = [
            ("Teléfono del cliente:", "numTelC", ""),
            ("Teléfono del vendedor:", "numTelV", ""),
            ("Total de pago:", "totalpago", ""),
            ("Código de barras:", "codigoBarras", "")
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
            ("Añadir", "#A2E4B8", self.crear_venta),
            ("Editar", "#FFE08A", self.editar_venta),
            ("Borrar", "#F4A4A4", self.borrar_venta)
        ]

        for i, (texto, color, comando) in enumerate(self.botones_principales):
            btn = tk.Button(frame_botones, text=texto, bg=color, font=("Arial", 12), command=comando)
            btn.grid(row=0, column=i, padx=5, ipadx=5, ipady=3)

        # Frame para la tabla
        frame_tabla = tk.Frame(self.root)
        frame_tabla.grid(row=10, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))

        # Treeview para mostrar ventas
        columnas = ("ID", "Teléfono cliente", "Teléfono vendedor", "Total pago", "Código barras")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100)

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_venta)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Posicionamiento
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mostrar_ventas(self):
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            self.cursor.execute(
                "SELECT idVenta, numTelC, numTelV, totalpago, codigoBarras FROM ventas ORDER BY idVenta")
            ventas = self.cursor.fetchall()

            for venta in ventas:
                self.tabla.insert("", "end", values=venta)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas: {str(e)}")

    def obtener_datos(self):
        return {clave: entry.get().strip() for clave, entry in self.campos.items()}

    def validar_datos(self, datos):
        # Validar teléfonos
        if not datos['numTelC'].isdigit() or len(datos['numTelC']) != 10:
            return "Teléfono del cliente debe tener 10 dígitos"

        if not datos['numTelV'].isdigit() or len(datos['numTelV']) != 10:
            return "Teléfono del vendedor debe tener 10 dígitos"

        # Validar total pago
        try:
            float(datos['totalpago'])
        except ValueError:
            return "Total de pago debe ser un número válido"

        # Validar código de barras
        if not datos['codigoBarras'].isdigit() or len(datos['codigoBarras']) != 13:
            return "Código de barras debe tener 13 dígitos"

        return None

    def crear_venta(self):
        datos = self.obtener_datos()

        # Validar campos vacíos
        campos_vacios = [nombre for nombre, valor in datos.items() if not valor]
        if campos_vacios:
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
            return

        # Validar formato de datos
        error_validacion = self.validar_datos(datos)
        if error_validacion:
            messagebox.showerror("Error", error_validacion)
            return

        try:
            self.conexion.start_transaction()

            # Verificar existencia de referencias
            self.cursor.execute("SELECT numTelC FROM cliente WHERE numTelC = %s", (datos['numTelC'],))
            if not self.cursor.fetchone():
                raise ValueError("El teléfono del cliente no está registrado")

            self.cursor.execute("SELECT numTelV FROM vendedor WHERE numTelV = %s", (datos['numTelV'],))
            if not self.cursor.fetchone():
                raise ValueError("El teléfono del vendedor no está registrado")

            self.cursor.execute("SELECT codigoBarras FROM articulos WHERE codigoBarras = %s", (datos['codigoBarras'],))
            if not self.cursor.fetchone():
                raise ValueError("El código de barras no existe")

            # Insertar venta
            self.cursor.execute("""
                INSERT INTO ventas (numTelC, numTelV, totalpago, codigoBarras)
                VALUES (%s, %s, %s, %s)
            """, (datos['numTelC'], datos['numTelV'], datos['totalpago'], datos['codigoBarras']))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Venta creada correctamente")
            self.mostrar_ventas()
            self.limpiar_campos()

        except mysql.connector.Error as err:
            self.conexion.rollback()
            if err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                messagebox.showerror("Error", "No existe la referencia (cliente, vendedor o artículo)")
            else:
                messagebox.showerror("Error", f"No se pudo crear la venta: {str(err)}")
        except ValueError as ve:
            self.conexion.rollback()
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            self.conexion.rollback()
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def limpiar_campos(self):
        """Limpia todos los campos de entrada"""
        for campo in self.campos.values():
            campo.delete(0, tk.END)

    def seleccionar_venta(self, event=None):
        seleccion = self.tabla.selection()
        if seleccion:
            item = self.tabla.item(seleccion[0])
            self.venta_seleccionada = item['values']
            self.id_original = item['values'][0]  # idVenta

            # Llena los campos con los datos
            self.limpiar_campos()
            self.campos['numTelC'].insert(0, item['values'][1])  # numTelC
            self.campos['numTelV'].insert(0, item['values'][2])  # numTelV
            self.campos['totalpago'].insert(0, item['values'][3])  # totalpago
            self.campos['codigoBarras'].insert(0, item['values'][4])  # codigoBarras

    def editar_venta(self):
        if not self.venta_seleccionada:
            messagebox.showerror("Error", "Seleccione una venta primero")
            return

        datos = self.obtener_datos()

        # Validar campos vacíos
        campos_vacios = [nombre for nombre, valor in datos.items() if not valor]
        if campos_vacios:
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
            return

        # Validar formato de datos
        error_validacion = self.validar_datos(datos)
        if error_validacion:
            messagebox.showerror("Error", error_validacion)
            return

        try:
            self.conexion.start_transaction()

            # Verificar existencia de referencias
            self.cursor.execute("SELECT numTelC FROM cliente WHERE numTelC = %s", (datos['numTelC'],))
            if not self.cursor.fetchone():
                raise ValueError("El teléfono del cliente no está registrado")

            self.cursor.execute("SELECT numTelV FROM vendedor WHERE numTelV = %s", (datos['numTelV'],))
            if not self.cursor.fetchone():
                raise ValueError("El teléfono del vendedor no está registrado")

            self.cursor.execute("SELECT codigoBarras FROM articulos WHERE codigoBarras = %s", (datos['codigoBarras'],))
            if not self.cursor.fetchone():
                raise ValueError("El código de barras no existe")

            # Actualizar venta
            self.cursor.execute("""
                UPDATE ventas 
                SET numTelC = %s, 
                    numTelV = %s, 
                    totalpago = %s, 
                    codigoBarras = %s 
                WHERE idVenta = %s
            """, (
                datos['numTelC'],
                datos['numTelV'],
                datos['totalpago'],
                datos['codigoBarras'],
                self.id_original
            ))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Venta actualizada correctamente")
            self.mostrar_ventas()
            self.limpiar_campos()
            self.venta_seleccionada = None
            self.id_original = None

        except mysql.connector.Error as err:
            self.conexion.rollback()
            if err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                messagebox.showerror("Error", "No existe la referencia (cliente, vendedor o artículo)")
            else:
                messagebox.showerror("Error", f"No se pudo actualizar la venta: {str(err)}")
        except ValueError as ve:
            self.conexion.rollback()
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            self.conexion.rollback()
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def borrar_venta(self):
        if not self.venta_seleccionada:
            messagebox.showerror("Error", "No se ha seleccionado una venta para borrar")
            return

        confirmacion = messagebox.askyesno("Confirmar", "¿Seguro que deseas borrar esta venta?")
        if not confirmacion:
            return

        try:
            self.conexion.start_transaction()

            id_venta = self.venta_seleccionada[0]
            self.cursor.execute("DELETE FROM ventas WHERE idVenta = %s", (id_venta,))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Venta borrada correctamente")
            self.mostrar_ventas()
            self.venta_seleccionada = None
            self.limpiar_campos()

        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo borrar la venta: {str(err)}")
        except Exception as e:
            self.conexion.rollback()
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def __del__(self):
        """Cierra la conexión a la base de datos al salir"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conexion'):
            self.conexion.close()