import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import re


class ClientesApp:
    def __init__(self, parent, main_root):
        self.parent = parent
        self.main_root = main_root
        self.root = parent
        self.root.configure(bg="#f0f2f5")  # Fondo claro y moderno

        self.cliente_seleccionado = None
        self.telefono_original = None

        try:
            self.conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysql",
                database="dbtiendaletty"
            )
            self.cursor = self.conexion.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{err}")
            return

        self.crear_tablas()
        self.configurar_interfaz()
        self.mostrar_clientes()

    def configurar_interfaz(self):
        # Configurar grid en root
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(5):
            self.root.grid_rowconfigure(i, weight=0)
        self.root.grid_rowconfigure(4, weight=1)  # Para que la tabla crezca

        # Título con fondo oscuro que abarca todo ancho
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 20))
        title_frame.grid_columnconfigure(0, weight=1)
        tk.Label(title_frame, text="Clientes", font=("Segoe UI", 24, "bold"), bg="#2c3e50", fg="white").grid(row=0, column=0, pady=20)

        # Campos de formulario alineados
        labels = ["Teléfono (10 dígitos):", "Nombre:", "Correo electrónico:"]
        keys = ["numTelC", "nombreC", "correo"]
        maxlens = [10, 50, 50]
        self.campos = {}

        for i, (label_text, key, maxlength) in enumerate(zip(labels, keys, maxlens), start=1):
            lbl = tk.Label(self.root, text=label_text, font=("Segoe UI", 11), bg="#f0f2f5", anchor="w")
            lbl.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(self.root, font=("Segoe UI", 11), bg="white", relief="groove", bd=2)
            entry.grid(row=i, column=1, columnspan=3, sticky="w", padx=10, pady=5)
            if maxlength:
                entry.configure(validate="key", validatecommand=(entry.register(self.validar_longitud), '%P', maxlength))
            self.campos[key] = entry

        # Botones alineados
        botones = [
            ("Añadir", "#27ae60", self.crear_cliente),
            ("Editar", "#f39c12", self.editar_cliente),
            ("Borrar", "#e74c3c", self.borrar_cliente),
            ("Limpiar", "#95a5a6", self.limpiar_campos)
        ]

        button_frame = tk.Frame(self.root, bg="#f0f2f5")
        button_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(10,20))
        for idx, (text, color, cmd) in enumerate(botones):
            btn = tk.Button(button_frame, text=text, command=cmd, bg=color, fg="white",
                            font=("Segoe UI", 11, "bold"), bd=0, relief="flat", padx=20, pady=8)
            btn.grid(row=0, column=idx, padx=10, ipadx=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.aclarar_color(b['bg'], 15)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

        # Tabla con scrollbar
        table_frame = tk.Frame(self.root, bg="#f0f2f5")
        table_frame.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=20, pady=(0,20))
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#34495e", foreground="white", padding=5)
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        style.map("Treeview", background=[("selected", "#3498db")])

        self.tabla = ttk.Treeview(table_frame,
                                  columns=("Teléfono", "Nombre", "Correo"),
                                  show="headings", selectmode="browse")

        columnas = [("Teléfono", 120, "center"),
                    ("Nombre", 250, "w"),
                    ("Correo", 200, "w")]

        for col, width, anchor in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Bind selección
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_cliente)

    def aclarar_color(self, color_hex, cantidad=30):
        try:
            r = min(255, int(color_hex[1:3], 16) + cantidad)
            g = min(255, int(color_hex[3:5], 16) + cantidad)
            b = min(255, int(color_hex[5:7], 16) + cantidad)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color_hex

    def validar_longitud(self, texto, maxlength):
        return len(texto) <= int(maxlength)

    def validar_email(self, email):
        if not email:
            return True
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def crear_tablas(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS cliente (
                    numTelC CHAR(10) PRIMARY KEY,
                    nombreC VARCHAR(50) NOT NULL,
                    correo VARCHAR(50)
                )
            """)
            self.conexion.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudieron crear las tablas:\n{err}")

    def mostrar_clientes(self):
        self.tabla.delete(*self.tabla.get_children())
        try:
            self.cursor.execute("SELECT numTelC, nombreC, correo FROM cliente ORDER BY nombreC")
            for cliente in self.cursor.fetchall():
                self.tabla.insert("", "end", values=(
                    cliente['numTelC'],
                    cliente['nombreC'],
                    cliente['correo'] or ""
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes:\n{err}")

    def obtener_datos(self):
        return {k: v.get().strip() for k, v in self.campos.items()}

    def validar_datos(self, datos):
        errores = []
        if not datos['numTelC']:
            errores.append("El teléfono es obligatorio")
        elif len(datos['numTelC']) != 10 or not datos['numTelC'].isdigit():
            errores.append("El teléfono debe tener 10 dígitos")
        if not datos['nombreC']:
            errores.append("El nombre es obligatorio")
        if datos['correo'] and not self.validar_email(datos['correo']):
            errores.append("El correo electrónico no tiene un formato válido")
        if errores:
            messagebox.showwarning("Validación", "\n".join(errores))
            return False
        return True

    def limpiar_campos(self):
        for campo in self.campos.values():
            campo.delete(0, tk.END)
        self.cliente_seleccionado = None
        self.telefono_original = None
        selection = self.tabla.selection()
        if selection:
            self.tabla.selection_remove(selection)

    def crear_cliente(self):
        datos = self.obtener_datos()
        if not self.validar_datos(datos):
            return
        try:
            self.cursor.execute("START TRANSACTION")
            self.cursor.execute("""
                INSERT INTO cliente (numTelC, nombreC, correo)
                VALUES (%s, %s, %s)
            """, (
                datos['numTelC'],
                datos['nombreC'],
                datos['correo'] if datos['correo'] else None
            ))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Cliente creado correctamente")
            self.mostrar_clientes()
            self.limpiar_campos()
        except mysql.connector.IntegrityError as err:
            self.conexion.rollback()
            if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                messagebox.showerror("Error", "El teléfono ya está registrado")
            else:
                messagebox.showerror("Error", f"Error de integridad:\n{err}")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo crear el cliente:\n{err}")

    def seleccionar_cliente(self, event):
        selected_items = self.tabla.selection()
        if selected_items:
            item_id = selected_items[0]
            item = self.tabla.item(item_id)
            self.cliente_seleccionado = item['values']
            self.telefono_original = item['values'][0]
            for campo in self.campos.values():
                campo.delete(0, tk.END)
            self.campos['numTelC'].insert(0, item['values'][0])
            self.campos['nombreC'].insert(0, item['values'][1])
            self.campos['correo'].insert(0, item['values'][2] if len(item['values']) > 2 else "")

    def editar_cliente(self):
        if not self.cliente_seleccionado:
            messagebox.showwarning("Error", "Seleccione un cliente para editar")
            return
        datos = self.obtener_datos()
        if not self.validar_datos(datos):
            return
        try:
            self.cursor.execute("START TRANSACTION")
            if datos['numTelC'] != self.telefono_original:
                self.cursor.execute("SELECT numTelC FROM cliente WHERE numTelC = %s", (datos['numTelC'],))
                if self.cursor.fetchone():
                    messagebox.showerror("Error", "El teléfono ya está registrado")
                    return
            self.cursor.execute("""
                UPDATE cliente 
                SET numTelC = %s, 
                    nombreC = %s, 
                    correo = %s 
                WHERE numTelC = %s
            """, (
                datos['numTelC'],
                datos['nombreC'],
                datos['correo'] if datos['correo'] else None,
                self.telefono_original
            ))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            self.mostrar_clientes()
            self.limpiar_campos()
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo actualizar el cliente:\n{err}")

    def borrar_cliente(self):
        if not self.cliente_seleccionado:
            messagebox.showwarning("Error", "Seleccione un cliente para borrar")
            return
        confirmacion = messagebox.askyesno(
            "Confirmar",
            f"¿Está seguro que desea eliminar al cliente:\n{self.cliente_seleccionado[1]}?"
        )
        if not confirmacion:
            return
        try:
            self.cursor.execute("START TRANSACTION")
            self.cursor.execute("DELETE FROM cliente WHERE numTelC = %s", (self.telefono_original,))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
            self.mostrar_clientes()
            self.limpiar_campos()
        except mysql.connector.Error as err:
            self.conexion.rollback()
            messagebox.showerror("Error", f"No se pudo eliminar el cliente:\n{err}")

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



