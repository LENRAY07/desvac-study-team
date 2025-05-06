import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from ModificarContrasenia import VentanaModificarContrasenia



class VendedoresApp:
    def __init__(self, parent, main_root):
        self.parent = parent
        self.main_root = main_root
        self.root = parent
        self.root.configure(bg="#5bfcfe")

        self.modo_edicion = False
        self.vendedor_seleccionado = None

        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="dbtiendaletty"
        )
        self.cursor = self.conexion.cursor()

        self.crear_tablas()
        self.crear_interfaz()
        self.mostrar_vendedores()


    def crear_tablas(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendedor (
                    numTelV CHAR(10) PRIMARY KEY,
                    nombreV VARCHAR(200),
                    horaEntrada TIME NULL,
                    horaSalida TIME NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS loginVendedor (
                    numTelV CHAR(10),
                    clave VARCHAR(100),
                    FOREIGN KEY (numTelV) REFERENCES vendedor(numTelV)
                )
            """)
            self.conexion.commit()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron crear las tablas: {e}")

    def crear_interfaz(self):
        self.root.grid_columnconfigure(2, weight=1)
        for i in range(7):
            self.root.grid_rowconfigure(i, weight=0)

        tk.Label(self.root, text="Vendedores", font=("Impact", 20, "bold"), bg="#5bfcfe"
                 ).grid(row=0, column=0, columnspan=3, pady=20)

        self.campos = {}
        etiquetas = [
            ("Teléfono:", "numTelV"),
            ("Nombre Completo:", "nombreV"),
            ("Hora Entrada (HH:MM):", "horaEntrada"),
            ("Hora Salida (HH:MM):", "horaSalida")
        ]

        for i, (texto, clave) in enumerate(etiquetas, 1):
            tk.Label(self.root, text=texto, font=("Arial", 14), bg="#5bfcfe"
                     ).grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entrada = tk.Entry(self.root, font=("Arial", 14), bg="#e6ffff")
            entrada.grid(row=i, column=2, padx=(0, 20), pady=10, sticky="ew")
            self.campos[clave] = entrada

        frame_botones = tk.Frame(self.root, bg="#5bfcfe")
        frame_botones.grid(row=5, column=0, columnspan=3, pady=20)

        botones = [
            ("Añadir", self.crear_vendedor, "#A2E4B8"),
            ("Editar", self.editar_vendedor, "#FFE08A"),
            ("Borrar", self.borrar_vendedor, "#F4A4A4")
        ]

        self.btn_modificar_clave = tk.Button(frame_botones, text="Modificar Contraseña", bg="#90CAF9",
                                             font=("Arial", 12), command=self.abrir_ventana_contrasenia)
        self.btn_modificar_clave.grid(row=0, column=4, padx=10, ipadx=10, ipady=5)

        for idx, (texto, comando, color) in enumerate(botones):
            tk.Button(frame_botones, text=texto, bg=color, font=("Arial", 12),
                      command=comando).grid(row=0, column=idx, padx=10, ipadx=10, ipady=5)

        # Treeview
        frame_tabla = tk.Frame(self.root)
        frame_tabla.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))

        self.tabla = ttk.Treeview(frame_tabla, columns=("Telefono", "Nombre", "Entrada", "Salida"), show="headings")
        for col in self.tabla["columns"]:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=150)

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_vendedor)
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mostrar_vendedores(self):
        self.tabla.delete(*self.tabla.get_children())
        try:
            self.cursor.execute("SELECT numTelV, nombreV, horaEntrada, horaSalida FROM vendedor ORDER BY nombreV")
            for vendedor in self.cursor.fetchall():
                datos = list(vendedor)
                # Convertir timedelta a string HH:MM
                datos[2] = str(datos[2])[:5] if datos[2] else ''
                datos[3] = str(datos[3])[:5] if datos[3] else ''
                self.tabla.insert("", "end", values=datos)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los vendedores: {e}")

    def obtener_datos(self):
        return {k: v.get().strip() for k, v in self.campos.items()}

    def limpiar_campos(self):
        for campo in self.campos.values():
            campo.delete(0, tk.END)
        self.vendedor_seleccionado = None

    def crear_vendedor(self):
        datos = self.obtener_datos()

        if not datos['numTelV'] or not datos['nombreV']:
            messagebox.showwarning("Advertencia", "Teléfono y nombre son campos obligatorios")
            return

        try:
            self.cursor.execute("""
                INSERT INTO vendedor (numTelV, nombreV, horaEntrada, horaSalida)
                VALUES (%s, %s, %s, %s)
            """, (datos['numTelV'], datos['nombreV'], datos['horaEntrada'], datos['horaSalida']))
            self.cursor.execute("""
                INSERT INTO loginVendedor (numTelV, clave)
                VALUES (%s, %s)
            """, (datos['numTelV'], datos['numTelV']))  # por defecto usar el teléfono como clave
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Vendedor y clave registrados correctamente")
            self.mostrar_vendedores()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el vendedor: {str(e)}")

    def abrir_ventana_contrasenia(self):
        if not self.vendedor_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un vendedor de la tabla primero.")
            return
        numTelV = self.vendedor_seleccionado[0]
        VentanaModificarContrasenia(self.root, self.cursor, self.conexion, numTelV)

    def seleccionar_vendedor(self, event):
        seleccion = self.tabla.focus()
        if seleccion:
            valores = self.tabla.item(seleccion, "values")
            self.vendedor_seleccionado = valores
            for i, clave in enumerate(["numTelV", "nombreV", "horaEntrada", "horaSalida"]):
                self.campos[clave].delete(0, tk.END)
                self.campos[clave].insert(0, valores[i])

    def borrar_vendedor(self):
        if not self.vendedor_seleccionado:
            messagebox.showerror("Error", "Selecciona un vendedor para borrar")
            return

        if messagebox.askyesno("Confirmar", "¿Desea borrar el vendedor?"):
            try:
                telefono = self.vendedor_seleccionado[0]
                self.cursor.execute("DELETE FROM loginVendedor WHERE numTelV=%s", (telefono,))
                self.cursor.execute("DELETE FROM vendedor WHERE numTelV=%s", (telefono,))
                self.conexion.commit()
                messagebox.showinfo("Éxito", "Vendedor eliminado")
                self.mostrar_vendedores()
                self.limpiar_campos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar: {e}")

    def editar_vendedor(self):
        if not self.vendedor_seleccionado:
            messagebox.showerror("Error", "Selecciona un vendedor para editar")
            return

        datos = self.obtener_datos()
        if not all(datos.values()):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return

        if len(datos['numTelV']) != 10 or not datos['numTelV'].isdigit():
            messagebox.showerror("Error", "Teléfono inválido")
            return

        try:
            self.cursor.execute("""
                UPDATE vendedor
                SET numTelV=%s, nombreV=%s, horaEntrada=%s, horaSalida=%s
                WHERE numTelV=%s
            """, (datos['numTelV'], datos['nombreV'], datos['horaEntrada'],
                  datos['horaSalida'], self.vendedor_seleccionado[0]))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Vendedor actualizado")
            self.mostrar_vendedores()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar: {e}")

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conexion'):
            self.conexion.close()

