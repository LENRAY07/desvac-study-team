import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errorcode


class VentasApp:
    def __init__(self, parent, main_root):
        self.parent = parent
        self.main_root = main_root
        self.root = parent
        self.root.configure(bg="#E9F1FA")

        # Variables de estado
        self.modo_edicion = False
        self.venta_seleccionada = None
        self.id_original = None

        # Conexión a MySQL
        try:
            self.conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysql",
                database="dbtiendaletty"
            )
            self.cursor = self.conexion.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {err}")
            return

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
                    FOREIGN KEY (codigoBarras) REFERENCES articulos(codigoBarras)
                )
            """)
            self.conexion.commit()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la tabla: {str(e)}")

    def crear_interfaz(self):
        self.root.configure(bg="#F2F6FC")

        frame_titulo = tk.Frame(self.root, bg="#2c3e50")
        frame_titulo.grid(row=0, column=0, columnspan=3, sticky="ew")
        tk.Label(
            frame_titulo, text="Ventas", bg="#2c3e50", fg="white",
            font=("Helvetica", 20, "bold"), pady=15
        ).pack()

        frame_entradas = tk.Frame(self.root, bg="#F2F6FC")
        frame_entradas.grid(row=1, column=0, columnspan=3, pady=15, padx=20, sticky="ew")

        self.campos = {}
        campos_config = [
            ("Teléfono del cliente:", "numTelC"),
            ("Teléfono del vendedor:", "numTelV"),
            ("Total de pago:", "totalpago"),
            ("Código de barras:", "codigoBarras")
        ]

        for i, (label_text, key) in enumerate(campos_config):
            tk.Label(
                frame_entradas, text=label_text, bg="#F2F6FC",
                font=("Arial", 12)
            ).grid(row=i, column=0, padx=10, pady=5, sticky="e")

            entry = tk.Entry(
                frame_entradas, font=("Arial", 12), bg="white",
                relief="groove", bd=2
            )
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            frame_entradas.grid_columnconfigure(1, weight=1)
            self.campos[key] = entry

        frame_botones = tk.Frame(self.root, bg="#F2F6FC")
        frame_botones.grid(row=2, column=0, columnspan=3, pady=10)

        botones = [
            ("Añadir", "#27AE60", self.crear_venta),
            ("Editar", "#F1C40F", self.editar_venta),
            ("Borrar", "#E74C3C", self.borrar_venta),
            ("Limpiar", "#7F8C8D", self.limpiar_campos)
        ]

        for i, (texto, color, comando) in enumerate(botones):
            tk.Button(
                frame_botones, text=texto, command=comando,
                bg=color, fg="white", font=("Arial", 11, "bold"),
                padx=15, pady=6, relief="flat", cursor="hand2"
            ).grid(row=0, column=i, padx=8)

        frame_tabla = tk.Frame(self.root, bg="#F2F6FC")
        frame_tabla.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        columnas = ("ID", "Teléfono cliente", "Teléfono vendedor", "Total pago", "Código barras")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_venta)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mostrar_ventas(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            self.cursor.execute("SELECT idVenta, numTelC, numTelV, totalpago, codigoBarras FROM ventas ORDER BY idVenta")
            ventas = self.cursor.fetchall()
            for venta in ventas:
                self.tabla.insert("", "end", values=venta)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas: {str(e)}")

    def obtener_datos(self):
        return {clave: entry.get().strip() for clave, entry in self.campos.items()}

    def validar_datos(self, datos):
        if not (datos['numTelC'].isdigit() and len(datos['numTelC']) == 10):
            return "Teléfono del cliente debe tener 10 dígitos numéricos"
        if not (datos['numTelV'].isdigit() and len(datos['numTelV']) == 10):
            return "Teléfono del vendedor debe tener 10 dígitos numéricos"
        try:
            float(datos['totalpago'])
        except ValueError:
            return "Total de pago debe ser un número válido"
        if not (datos['codigoBarras'].isdigit() and len(datos['codigoBarras']) == 13):
            return "Código de barras debe tener 13 dígitos numéricos"
        return None

    def crear_venta(self):
        datos = self.obtener_datos()
        if any(not v for v in datos.values()):
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
            return
        error = self.validar_datos(datos)
        if error:
            messagebox.showerror("Error", error)
            return
        try:
            # Validar que existan las referencias antes de empezar la transacción
            self.cursor.execute("SELECT numTelC FROM cliente WHERE numTelC = %s", (datos['numTelC'],))
            if not self.cursor.fetchone():
                messagebox.showerror("Error", "El teléfono del cliente no está registrado")
                return
            self.cursor.execute("SELECT numTelV FROM vendedor WHERE numTelV = %s", (datos['numTelV'],))
            if not self.cursor.fetchone():
                messagebox.showerror("Error", "El teléfono del vendedor no está registrado")
                return
            self.cursor.execute("SELECT codigoBarras FROM articulos WHERE codigoBarras = %s", (datos['codigoBarras'],))
            if not self.cursor.fetchone():
                messagebox.showerror("Error", "El código de barras no existe")
                return

            self.conexion.autocommit = False
            self.cursor.execute(
                "INSERT INTO ventas (numTelC, numTelV, totalpago, codigoBarras) VALUES (%s, %s, %s, %s)",
                (datos['numTelC'], datos['numTelV'], datos['totalpago'], datos['codigoBarras'])
            )
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Venta creada correctamente")
            self.mostrar_ventas()
            self.limpiar_campos()
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo crear la venta: {str(err)}")
        finally:
            self.conexion.autocommit = True

    def seleccionar_venta(self, event=None):
        selected = self.tabla.selection()
        if not selected:
            return
        item = self.tabla.item(selected[0])
        self.venta_seleccionada = item['values']
        self.id_original = item['values'][0]
        self.limpiar_campos()
        self.campos['numTelC'].insert(0, item['values'][1])
        self.campos['numTelV'].insert(0, item['values'][2])
        self.campos['totalpago'].insert(0, item['values'][3])
        self.campos['codigoBarras'].insert(0, item['values'][4])

    def editar_venta(self):
        if not self.venta_seleccionada:
            messagebox.showerror("Error", "Seleccione una venta primero")
            return
        datos = self.obtener_datos()
        if any(not v for v in datos.values()):
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
            return
        error = self.validar_datos(datos)
        if error:
            messagebox.showerror("Error", error)
            return
        try:
            # Validar referencias
            self.cursor.execute("SELECT numTelC FROM cliente WHERE numTelC = %s", (datos['numTelC'],))
            if not self.cursor.fetchone():
                messagebox.showerror("Error", "El teléfono del cliente no está registrado")
                return
            self.cursor.execute("SELECT numTelV FROM vendedor WHERE numTelV = %s", (datos['numTelV'],))
            if not self.cursor.fetchone():
                messagebox.showerror("Error", "El teléfono del vendedor no está registrado")
                return
            self.cursor.execute("SELECT codigoBarras FROM articulos WHERE codigoBarras = %s", (datos['codigoBarras'],))
            if not self.cursor.fetchone():
                messagebox.showerror("Error", "El código de barras no existe")
                return

            self.conexion.autocommit = False
            self.cursor.execute("""
                UPDATE ventas 
                SET numTelC = %s, numTelV = %s, totalpago = %s, codigoBarras = %s
                WHERE idVenta = %s
            """, (datos['numTelC'], datos['numTelV'], datos['totalpago'], datos['codigoBarras'], self.id_original))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Venta actualizada correctamente")
            self.mostrar_ventas()
            self.limpiar_campos()
            self.venta_seleccionada = None
            self.id_original = None
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo actualizar la venta: {str(err)}")
        finally:
            self.conexion.autocommit = True

    def borrar_venta(self):
        if not self.venta_seleccionada:
            messagebox.showerror("Error", "No se ha seleccionado una venta para borrar")
            return
        confirmacion = messagebox.askyesno("Confirmar", "¿Seguro que deseas borrar esta venta?")
        if not confirmacion:
            return
        try:
            self.conexion.autocommit = False
            self.cursor.execute("DELETE FROM ventas WHERE idVenta = %s", (self.venta_seleccionada[0],))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Venta borrada correctamente")
            self.mostrar_ventas()
            self.limpiar_campos()
            self.venta_seleccionada = None
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo borrar la venta: {str(err)}")
        finally:
            self.conexion.autocommit = True

    def limpiar_campos(self):
        for campo in self.campos.values():
            campo.delete(0, tk.END)

    def __del__(self):
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'conexion') and self.conexion.is_connected():
                self.conexion.close()
        except:
            pass
