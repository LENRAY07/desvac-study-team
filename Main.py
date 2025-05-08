import tkinter as tk
from tkinter import messagebox
import mysql.connector
from CRUD_Clientes import ClientesApp
from CRUD_Proveedores import ProveedoresApp
from CRUD_Vendedor import VendedoresApp
from CRUD_Articulos import ArticulosApp
from CRUD_Ventas import VentasApp
from MenuIInicio import InicioApp


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.configurar_ventana_principal()
        self.vendedor_logueado = None
        self.conexion_db = self.conectar_base_datos()

        self.crear_barra_navegacion()
        self.crear_contenedor_principal()
        self.inicializar_modulos()

        # Mostrar módulo inicial
        self.mostrar_inicio()

    def configurar_ventana_principal(self):
        """Configura la ventana principal con dimensiones y posición centrada"""
        self.root.title("Sistema de Gestión Tienda Letty")
        self.root.geometry("1200x700")
        self.root.configure(bg="#E9F1FA")

        # Centrar ventana
        ancho_ventana = 1200
        alto_ventana = 700
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()
        x = (ancho_pantalla // 2) - (ancho_ventana // 2)
        y = (alto_pantalla // 2) - (alto_ventana // 2)
        self.root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    def conectar_base_datos(self):
        """Establece y retorna la conexión a la base de datos"""
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysql",
                database="dbtiendaletty"
            )
        except mysql.connector.Error as err:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{err}")
            self.root.destroy()
            raise

    def crear_barra_navegacion(self):
        """Crea la barra de navegación superior con botones para cada módulo"""
        self.nav_frame = tk.Frame(self.root, bg="#E9F1FA")
        self.nav_frame.pack(fill="x", pady=(0, 5))

        # Configuración de botones
        botones_nav = [
            ("Menú Principal", self.mostrar_inicio, "#E9F1FA"),
            ("Proveedores", self.mostrar_proveedores, "#DAF7A6"),
            ("Clientes", self.mostrar_clientes, "#f4d03f"),
            ("Vendedores", self.mostrar_vendedores, "#f5b041"),
            ("Artículos", self.mostrar_articulos, "#e74c3c"),
            ("Ventas", self.mostrar_ventas, "#cd6155")
        ]

        for texto, comando, color in botones_nav:
            tk.Button(
                self.nav_frame,
                text=texto,
                command=comando,
                bg=color,
                fg="black",
                relief="flat",
                font=("Arial", 10, "bold"),
                padx=15,
                pady=5
            ).pack(side="left", padx=2)

    def crear_contenedor_principal(self):
        """Crea el contenedor principal donde se mostrarán los módulos"""
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

    def inicializar_modulos(self):
        """Inicializa todos los módulos de la aplicación"""
        self.frame_proveedores = tk.Frame(self.container)
        self.proveedores_app = ProveedoresApp(self.frame_proveedores, self.root)

        self.frame_clientes = tk.Frame(self.container)
        self.clientes_app = ClientesApp(self.frame_clientes, self.root)

        self.frame_vendedor = tk.Frame(self.container)
        self.vendedores_app = VendedoresApp(self.frame_vendedor, self.root)

        self.frame_articulos = tk.Frame(self.container)
        self.articulos_app = ArticulosApp(self.frame_articulos, self.root)

        self.frame_ventas = tk.Frame(self.container)
        self.ventas_app = VentasApp(self.frame_ventas, self.root)

        self.frame_inicio = tk.Frame(self.container)
        self.inicio_app = InicioApp(self.frame_inicio, self.root)


    def ocultar_todos_los_frames(self):
        """Oculta todos los frames de los módulos"""
        for frame in [
            self.frame_proveedores,
            self.frame_clientes,
            self.frame_vendedor,
            self.frame_articulos,
            self.frame_ventas,
            self.frame_inicio,
        ]:
            frame.pack_forget()

    def mostrar_proveedores(self):
        """Muestra el módulo de proveedores"""
        self.ocultar_todos_los_frames()
        self.frame_proveedores.pack(fill="both", expand=True)
        self.root.title("Proveedores - Sistema de Gestión Tienda Letty")
        self.proveedores_app.mostrar_proveedores()

    def mostrar_clientes(self):
        """Muestra el módulo de clientes"""
        self.ocultar_todos_los_frames()
        self.frame_clientes.pack(fill="both", expand=True)
        self.root.title("Clientes - Sistema de Gestión Tienda Letty")
        self.clientes_app.mostrar_clientes()

    def mostrar_inicio(self):
        self.ocultar_todos_los_frames()
        self.frame_inicio.pack(fill="both", expand=True)
        self.root.title("Home - Sistema de Gestión Tienda Letty")

    def mostrar_vendedores(self):
        """Muestra el módulo de vendedores"""
        self.ocultar_todos_los_frames()
        self.frame_vendedor.pack(fill="both", expand=True)
        self.root.title("Vendedores - Sistema de Gestión Tienda Letty")

    def mostrar_articulos(self):
        """Muestra el módulo de artículos"""
        self.ocultar_todos_los_frames()
        self.frame_articulos.pack(fill="both", expand=True)
        self.root.title("Artículos - Sistema de Gestión Tienda Letty")

    def mostrar_ventas(self):
        """Muestra el módulo de ventas con autenticación previa"""
        if not self.vendedor_logueado:
            self.mostrar_login_vendedor()
        else:
            self.ocultar_todos_los_frames()
            self.frame_ventas.pack(fill="both", expand=True)
            self.root.title(f"Ventas - Sesión de {self.vendedor_logueado}")
            self.ventas_app.mostrar_ventas()

    def mostrar_login_vendedor(self):
        """Muestra la ventana de login para vendedores con diseño mejorado"""
        login_window = tk.Toplevel(self.root)
        login_window.title("Inicio de sesión - Vendedores")
        login_window.geometry("450x350")
        login_window.resizable(False, False)
        login_window.configure(bg="#f0f8ff")  # Mismo fondo que las otras interfaces
        login_window.grab_set()  # Hace la ventana modal

        # Centrar ventana
        self.centrar_ventana(login_window, self.root)

        # Frame principal
        main_frame = tk.Frame(login_window, bg="#f0f8ff", padx=30, pady=30)
        main_frame.pack(fill="both", expand=True)

        # Título con estilo consistente
        tk.Label(main_frame, text="Inicio de Sesión",
                 font=("Helvetica", 18, "bold"),
                 bg="#f0f8ff", fg="#2c3e50").pack(pady=(0, 20))

        # Frame del formulario con estilo
        form_frame = tk.Frame(main_frame, bg="#ffffff", padx=20, pady=20,
                              relief="groove", borderwidth=2)
        form_frame.pack(fill="x", pady=(0, 20))

        # Campo de teléfono
        tk.Label(form_frame, text="Teléfono:",
                 font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.entry_tel = tk.Entry(form_frame, font=("Arial", 12),
                                  relief="solid", borderwidth=1,
                                  highlightthickness=1,
                                  highlightbackground="#d3d3d3",
                                  highlightcolor="#3498db")
        self.entry_tel.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        # Campo de contraseña
        tk.Label(form_frame, text="Contraseña:",
                 font=("Arial", 11), bg="#ffffff").grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.entry_clave = tk.Entry(form_frame, font=("Arial", 12), show="*",
                                    relief="solid", borderwidth=1,
                                    highlightthickness=1,
                                    highlightbackground="#d3d3d3",
                                    highlightcolor="#3498db")
        self.entry_clave.grid(row=3, column=0, sticky="ew", pady=(0, 15))

        # Frame para botones
        btn_frame = tk.Frame(main_frame, bg="#f0f8ff")
        btn_frame.pack()

        # Botón de ingreso con estilo moderno
        tk.Button(btn_frame, text="Ingresar",
                  font=("Arial", 12, "bold"),
                  bg="#2ecc71", fg="white",
                  activebackground=self.aclarar_color("#2ecc71", 20),
                  activeforeground="white",
                  relief="flat", padx=25, pady=8,
                  command=lambda: self.verificar_credenciales(
                      self.entry_tel.get(),
                      self.entry_clave.get(),
                      login_window)
                  ).grid(row=0, column=0, padx=5)

        # Botón de cancelar
        tk.Button(btn_frame, text="Cancelar",
                  font=("Arial", 12, "bold"),
                  bg="#e74c3c", fg="white",
                  activebackground=self.aclarar_color("#e74c3c", 20),
                  activeforeground="white",
                  relief="flat", padx=25, pady=8,
                  command=login_window.destroy
                  ).grid(row=0, column=1, padx=5)

        # Configurar grid
        form_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        # Enfoque en el campo de teléfono
        self.entry_tel.focus_set()

        # Manejar cierre de ventana
        login_window.protocol("WM_DELETE_WINDOW", login_window.destroy)

    def centrar_ventana(self, ventana, parent):
        """Centra la ventana con respecto a la ventana padre"""
        ventana.update_idletasks()
        width = ventana.winfo_width()
        height = ventana.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        ventana.geometry(f"+{x}+{y}")

    def aclarar_color(self, color_hex, cantidad=30):
        """Aclara un color hexadecimal para efecto hover (consistente con otras ventanas)"""
        try:
            r = min(255, int(color_hex[1:3], 16) + cantidad)
            g = min(255, int(color_hex[3:5], 16) + cantidad)
            b = min(255, int(color_hex[5:7], 16) + cantidad)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color_hex

    def verificar_credenciales(self, telefono, clave, ventana):
        """Verifica las credenciales del vendedor contra la base de datos"""
        # Validaciones iniciales
        if not telefono or not clave:
            messagebox.showwarning("Campos vacíos",
                                   "Todos los campos son obligatorios",
                                   parent=ventana)
            return

        if len(telefono) != 10 or not telefono.isdigit():
            messagebox.showwarning("Teléfono inválido",
                                   "El teléfono debe tener 10 dígitos",
                                   parent=ventana)
            return

        try:
            cursor = self.conexion_db.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.numTelV, v.nombreV 
                FROM loginVendedor l
                JOIN vendedor v ON l.numTelV = v.numTelV
                WHERE l.numTelV = %s AND l.clave = %s
            """, (telefono, clave))

            resultado = cursor.fetchone()
            cursor.close()

            if resultado:
                self.vendedor_logueado = f"{resultado['nombreV']} ({resultado['numTelV']})"
                ventana.destroy()
                self.mostrar_ventas()
                messagebox.showinfo("Bienvenido",
                                    f"Bienvenido {resultado['nombreV']}",
                                    parent=self.root)
            else:
                messagebox.showerror("Error",
                                     "Credenciales inválidas",
                                     parent=ventana)
        except mysql.connector.Error as err:
            messagebox.showerror("Error",
                                 f"Error al verificar credenciales:\n{err}",
                                 parent=ventana)

    def __del__(self):
        """Cierra la conexión a la base de datos al salir"""
        if hasattr(self, 'conexion_db') and self.conexion_db.is_connected():
            self.conexion_db.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()