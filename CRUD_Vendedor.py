import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from ModificarContrasenia import VentanaModificarContrasenia


class VendedoresApp:
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
        self.root.grid_columnconfigure(1, weight=1)
        for i in range(7):
            self.root.grid_rowconfigure(i, weight=0)

        # Título con estilo moderno
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        title_frame.grid_columnconfigure(0, weight=1)

        tk.Label(title_frame, text="Vendedores", font=("Segoe UI", 24, "bold"),
                 bg="#2c3e50", fg="white").grid(row=0, column=0, pady=20)

        # Frame principal para los campos
        form_frame = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=10)
        form_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.campos = {}
        etiquetas = [
            ("Teléfono:", "numTelV"),
            ("Nombre Completo:", "nombreV"),
            ("Hora Entrada (HH:MM):", "horaEntrada"),
            ("Hora Salida (HH:MM):", "horaSalida")
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

        # Botones con estilo moderno
        action_buttons = [
            ("Añadir", self.crear_vendedor, "#27ae60"),
            ("Editar", self.editar_vendedor, "#f39c12"),
            ("Borrar", self.borrar_vendedor, "#e74c3c"),
            ("Modificar Contraseña", self.abrir_ventana_contrasenia, "#3498db")
        ]

        for idx, (texto, comando, color) in enumerate(action_buttons):
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

        # Treeview con estilo moderno
        self.tabla = ttk.Treeview(table_frame, columns=("Telefono", "Nombre", "Entrada", "Salida"),
                                  show="headings", height=8, style="Custom.Treeview")

        # Configurar columnas
        column_widths = {"Telefono": 120, "Nombre": 200, "Entrada": 100, "Salida": 100}
        for col in self.tabla["columns"]:
            self.tabla.heading(col, text=col, anchor="w")
            self.tabla.column(col, width=column_widths.get(col, 100), anchor="w")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_vendedor)

    def lighten_color(self, color, amount=0.2):
        """Aclara un color hexadecimal"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        lighter = tuple(min(255, int(c + (255 - c) * amount)) for c in rgb)
        return f'#{lighter[0]:02x}{lighter[1]:02x}{lighter[2]:02x}'

    def mostrar_vendedores(self):
        self.tabla.delete(*self.tabla.get_children())
        try:
            self.cursor.execute("SELECT numTelV, nombreV, horaEntrada, horaSalida FROM vendedor ORDER BY nombreV")
            for vendedor in self.cursor.fetchall():
                datos = list(vendedor)
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


