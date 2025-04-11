import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


class VendedoresApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vendedores")
        self.root.geometry("1000x600")
        self.root.configure(bg="#5bfcfe")

        # Variables de estado
        self.modo_edicion = False
        self.vendedor_seleccionado = None
        self.telefono_original = None

        # Conexión a MySQL
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="dbtiendaletty"
        )
        self.cursor = self.conexion.cursor()

        self.crear_interfaz()
        self.crear_tabla_vendedor()
        self.mostrar_vendedores()

    def crear_tabla_vendedor(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendedor (
                    numTelV CHAR(10) PRIMARY KEY,
                    nombreV VARCHAR(70),
                    horaEntrada TIME NULL
                    )
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
        for i in range(6):
            self.root.grid_rowconfigure(i, weight=0)
        self.root.grid_rowconfigure(6, weight=1)

        # Título
        tk.Label(self.root, text="Vendedores", font=("Impact", 20, "bold"), bg="#5bfcfe"
                 ).grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

        # Campos de entrada
        self.campos = {}
        campos_config = [
            ("Teléfono:", "numTelV", ""),
            ("Nombre:", "nombreV", ""),
            ("Hora Entrada (HH:MM):", "horaEntrada", "")
        ]

        for i, (texto, nombre, show_char) in enumerate(campos_config, start=1):
            tk.Label(self.root, text=texto, font=("Arial", 14), bg="#5bfcfe"
                     ).grid(row=i, column=0, padx=10, pady=10, sticky="w")

            entry = tk.Entry(self.root, font=("Arial", 14), bg="#e6ffff", show=show_char)
            entry.grid(row=i, column=2, padx=(0, 20), pady=10, sticky="ew")
            self.campos[nombre] = entry

        # Frame para botones principales
        frame_botones_principales = tk.Frame(self.root, bg="#5bfcfe")
        frame_botones_principales.grid(row=5, column=0, columnspan=3, pady=20)

        # Botones CRUD principales
        self.btn_crear = tk.Button(frame_botones_principales, text="Crear", bg="#A2E4B8",
                                   font=("Arial", 12), command=self.crear_vendedor)
        self.btn_crear.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)

        self.btn_leer = tk.Button(frame_botones_principales, text="Leer", bg="#9AD0F5",
                                  font=("Arial", 12), command=self.mostrar_detalles_vendedor)
        self.btn_leer.grid(row=0, column=1, padx=10, ipadx=10, ipady=5)

        self.btn_editar = tk.Button(frame_botones_principales, text="Editar", bg="#FFE08A",
                                    font=("Arial", 12), command=self.preparar_edicion)
        self.btn_editar.grid(row=0, column=2, padx=10, ipadx=10, ipady=5)

        self.btn_borrar = tk.Button(frame_botones_principales, text="Borrar", bg="#F4A4A4",
                                    font=("Arial", 12), command=self.borrar_vendedor)
        self.btn_borrar.grid(row=0, column=3, padx=10, ipadx=10, ipady=5)

        # Frame para botones secundarios (confirmar/cancelar/volver)
        self.frame_botones_secundarios = tk.Frame(self.root, bg="#5bfcfe")
        self.frame_botones_secundarios.grid(row=7, column=0, columnspan=3, pady=10)
        self.frame_botones_secundarios.grid_remove()  # Ocultar inicialmente

        self.btn_confirmar = tk.Button(self.frame_botones_secundarios, text="Confirmar", bg="#A2E4B8",
                                       font=("Arial", 12), command=self.confirmar_actualizacion)
        self.btn_confirmar.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)

        self.btn_cancelar = tk.Button(self.frame_botones_secundarios, text="Cancelar", bg="#F4A4A4",
                                      font=("Arial", 12), command=self.cancelar_edicion)
        self.btn_cancelar.grid(row=0, column=1, padx=10, ipadx=10, ipady=5)

        self.btn_volver = tk.Button(self.frame_botones_secundarios, text="Volver a lista", bg="#9AD0F5",
                                    font=("Arial", 12), command=self.volver_a_lista)
        self.btn_volver.grid(row=0, column=2, padx=10, ipadx=10, ipady=5)

        # Treeview
        frame_tabla = tk.Frame(self.root)
        frame_tabla.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))

        self.tabla = ttk.Treeview(frame_tabla, columns=("Nombre",), show="headings")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.column("Nombre", width=300)



        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mostrar_vendedores(self):
        """Muestra todos los vendedores en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            self.cursor.execute("SELECT nombreV FROM vendedor ORDER BY nombreV")
            vendedores = self.cursor.fetchall()

            for vendedor in vendedores:
                self.tabla.insert("", "end", values=vendedor)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los vendedores: {str(e)}")

    def crear_vendedor(self):
        """Crea un nuevo vendedor"""
        datos = {
            'numTelV': self.campos['numTelV'].get(),
            'nombreV': self.campos['nombreV'].get(),
            'horaEntrada': self.campos['horaEntrada'].get()
        }

        # Validación básica
        if not datos['numTelV'] or not datos['nombreV']:
            messagebox.showwarning("Advertencia", "Teléfono y nombre son campos obligatorios")
            return

        try:
            self.cursor.execute("""
                INSERT INTO vendedor (numTelV, nombreV, horaEntrada)
                VALUES (%s, %s, %s)
            """, (datos['numTelV'], datos['nombreV'], datos['horaEntrada']))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Vendedor creado correctamente")
            self.volver_a_lista()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el vendedor: {str(e)}")

    def mostrar_detalles_vendedor(self):
        """Muestra los detalles del vendedor seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un vendedor primero")
            return

        telefono = self.tabla.item(seleccion[0])['values'][0]

        try:
            self.cursor.execute("SELECT * FROM vendedor WHERE nombreV = %s", (telefono,))
            vendedor = self.cursor.fetchone()

            if vendedor:
                # Configurar columnas para mostrar detalles
                self.tabla["columns"] = ("Teléfono", "Nombre", "Hora Entrada")

                # Configurar encabezados
                columnas = [
                    ("Teléfono", 150),
                    ("Nombre", 250),
                    ("Hora Entrada", 150)
                ]

                for col, width in columnas:
                    self.tabla.heading(col, text=col)
                    self.tabla.column(col, width=width)

                # Limpiar tabla y mostrar solo este vendedor
                for item in self.tabla.get_children():
                    self.tabla.delete(item)

                self.tabla.insert("", "end", values=vendedor)
                self.vendedor_seleccionado = vendedor

                # Mostrar botón "Volver a lista"
                self.frame_botones_secundarios.grid()
                self.btn_volver.config(state=tk.NORMAL)
                self.btn_confirmar.config(state=tk.DISABLED)
                self.btn_cancelar.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Información", "No se encontraron detalles para este vendedor")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles: {str(e)}")

    def preparar_edicion(self):
        """Prepara la interfaz para editar un vendedor"""
        if not self.vendedor_seleccionado:
            messagebox.showwarning("Advertencia", "Primero use 'Leer' en un vendedor")
            return

        # Cargar datos en los campos
        self.limpiar_campos()
        self.campos['numTelV'].insert(0, self.vendedor_seleccionado[0])
        self.campos['nombreV'].insert(0, self.vendedor_seleccionado[1])
        self.campos['horaEntrada'].insert(0, self.vendedor_seleccionado[2] or "")

        # Cambiar a modo edición
        self.modo_edicion = True
        self.telefono_original = self.vendedor_seleccionado[0]

        # Mostrar botones de confirmación
        self.frame_botones_secundarios.grid()
        self.btn_confirmar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.NORMAL)
        self.btn_volver.config(state=tk.DISABLED)

        # Deshabilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.DISABLED)

    def confirmar_actualizacion(self):
        """Confirma la actualización del vendedor"""
        datos = {
            'telefono_original': self.telefono_original,
            'numTelV': self.campos['numTelV'].get(),
            'nombreV': self.campos['nombreV'].get(),
            'horaEntrada': self.campos['horaEntrada'].get()
        }

        # Validar campos vacíos
        if not datos['numTelV'] or not datos['nombreV']:
            messagebox.showwarning("Error", "Teléfono y nombre son campos obligatorios")
            return

        try:
            # Verificar si el nuevo teléfono ya existe (si cambió)
            if datos['numTelV'] != datos['telefono_original']:
                self.cursor.execute("SELECT COUNT(*) FROM vendedor WHERE numTelV = %s", (datos['numTelV'],))
                if self.cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "El nuevo número de teléfono ya existe")
                    return

            # Actualizar el vendedor
            self.cursor.execute("""
                UPDATE vendedor 
                SET numTelV = %s, nombreV = %s, horaEntrada = %s
                WHERE numTelV = %s
            """, (datos['numTelV'], datos['nombreV'], datos['horaEntrada'], datos['telefono_original']))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Vendedor actualizado correctamente")
            self.cancelar_edicion()
            self.volver_a_lista()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el vendedor: {str(e)}")

    def cancelar_edicion(self):
        """Cancela el modo de edición"""
        # Limpiar todos los campos, incluyendo el teléfono
        for nombre, campo in self.campos.items():
            campo.config(state='normal')  # Habilitar temporalmente para limpiar
            campo.delete(0, tk.END)

        self.modo_edicion = False
        self.telefono_original = None

        # Ocultar botones secundarios
        self.frame_botones_secundarios.grid_remove()

        # Habilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.NORMAL)

    def volver_a_lista(self):
        self.tabla["columns"]=("Nombre")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.column("Nombre", width=200)

        """Vuelve a mostrar la lista de vendedores"""
        self.mostrar_vendedores()
        self.vendedor_seleccionado = None
        self.frame_botones_secundarios.grid_remove()

        # Habilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.NORMAL)

    def borrar_vendedor(self):
        """Borra un vendedor existente"""
        if not self.vendedor_seleccionado:
            messagebox.showwarning("Advertencia", "Primero use 'Leer' en un vendedor")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de borrar este vendedor?"):
            try:
                self.cursor.execute("DELETE FROM vendedor WHERE numTelV = %s", (self.vendedor_seleccionado[0],))
                self.conexion.commit()
                messagebox.showinfo("Éxito", "Vendedor borrado correctamente")
                self.volver_a_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar el vendedor: {str(e)}")

    def limpiar_campos(self):
        """Limpia todos los campos de entrada, incluso los deshabilitados"""
        for nombre, campo in self.campos.items():
            estado_actual = campo['state']  # Guardar estado actual
            campo.config(state='normal')  # Habilitar temporalmente
            campo.delete(0, tk.END)  # Limpiar contenido
            campo.config(state=estado_actual)  # Restaurar estado original

    def __del__(self):
        """Cierra la conexión a la base de datos al salir"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conexion'):
            self.conexion.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = VendedoresApp(root)
    root.mainloop()