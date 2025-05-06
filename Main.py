import tkinter as tk

from CRUD_Clientes import ClientesApp
from CRUD_Proveedores import ProveedoresApp # Importar desde archivo separado
from CRUD_Vendedor import VendedoresApp
from CRUD_Articulos import ArticulosApp
from CRUD_Ventas import VentasApp


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de la tienda")  # Título general aquí
        self.root.geometry("1200x700")

        ancho_ventana = 1200
        alto_ventana = 700

        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()

        x = (ancho_pantalla // 2) - (ancho_ventana // 2)
        y = (alto_pantalla // 2) - (alto_ventana // 2)

        self.root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        # Barra de navegación
        nav_frame = tk.Frame(self.root, bg="#5bfcfe")
        nav_frame.pack(fill="x")


        # Botón para mostrar proveedores
        btn_proveedores = tk.Button(
            nav_frame,
            text="Proveedores",
            command=self.mostrar_proveedores,
            bg="#ffffff",
            fg="black"
        )
        btn_proveedores.pack(side="left")

        btn_clientes = tk.Button(
            nav_frame,
            text="Clientes",
            command=self.mostrar_clientes,
            bg="#ffffff",
            fg="black"
        )
        btn_clientes.pack(side="left")

        btn_vendedores = tk.Button(
            nav_frame,
            text="Vendedores",
            command=self.mostrar_vendedores,
            bg="#ffffff",
            fg="black"
        )
        btn_vendedores.pack(side="left")

        btn_articulos = tk.Button(
            nav_frame,
            text="Articulos",
            command=self.mostrar_articulos,
            bg="#ffffff",
            fg="black"
        )
        btn_articulos.pack(side="left")

        btn_ventas = tk.Button(
            nav_frame,
            text="Ventas",
            command=self.mostrar_ventas,
            bg="#ffffff",
            fg="black"
        )
        btn_ventas.pack(side="left")

        # Contenedor principal
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)



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
        # Mostrar inicialmente
        self.mostrar_proveedores()
        self.vendedor_logueado = None

    def ocultar_todos_los_frames(self):
        self.frame_proveedores.pack_forget()
        self.frame_clientes.pack_forget()
        self.frame_vendedor.pack_forget()
        self.frame_articulos.pack_forget()
        self.frame_ventas.pack_forget()

    def mostrar_proveedores(self):
        # Ocultar otros frames si los hay
        self.ocultar_todos_los_frames()
        self.frame_proveedores.pack(fill="both", expand=True)
        self.root.title("Proveedores - Sistema de Gestión")  # Cambiar título aquí

    def mostrar_clientes(self):

        self.ocultar_todos_los_frames()
        self.frame_clientes.pack(fill="both", expand=True)
        self.root.title("Clientes - Sistema de Gestión")

    def mostrar_vendedores(self):

        self.ocultar_todos_los_frames()
        self.frame_vendedor.pack(fill="both", expand=True)
        self.root.title("Vendedores - Sistema de Gestión")

    def mostrar_articulos(self):
        self.ocultar_todos_los_frames()
        self.frame_articulos.pack(fill="both", expand=True)

    def mostrar_ventas(self):
        if not self.vendedor_logueado:
            self.mostrar_login_vendedor()
        else:
            self.ocultar_todos_los_frames()
            self.frame_ventas.pack(fill="both", expand=True)
            self.root.title(f"Ventas - Sesión de {self.vendedor_logueado}")

    def mostrar_login_vendedor(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Iniciar sesión como vendedor")
        login_window.geometry("300x200")
        login_window.configure(bg="#5bfcfe")

        frame = tk.Frame(login_window, bg="#5bfcfe")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="Teléfono:", bg="#5bfcfe").pack()
        entry_tel = tk.Entry(frame)
        entry_tel.pack()

        tk.Label(frame, text="Clave:", bg="#5bfcfe").pack()
        entry_clave = tk.Entry(frame, show="*")
        entry_clave.pack()

        def verificar_credenciales():
            tel = entry_tel.get()
            clave = entry_clave.get()
            import mysql.connector
            try:
                conexion = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="mysql",
                    database="dbtiendaletty"
                )
                cursor = conexion.cursor()
                cursor.execute("SELECT * FROM loginVendedor WHERE numTelV = %s AND clave = %s", (tel, clave))
                if cursor.fetchone():
                    self.vendedor_logueado = tel
                    login_window.destroy()
                    self.mostrar_ventas()
                else:
                    tk.messagebox.showerror("Error", "Credenciales inválidas")
                cursor.close()
                conexion.close()
            except Exception as e:
                tk.messagebox.showerror("Error", f"No se pudo conectar: {e}")

        tk.Button(login_window, text="Ingresar", bg="#A2E4B8", command=verificar_credenciales).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()