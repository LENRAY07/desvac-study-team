import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime


class ArticulosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Artículos")
        self.root.geometry("1000x700")
        self.root.configure(bg="#5bfcfe")

        # Variables de estado
        self.modo_edicion = False
        self.articulo_seleccionado = None
        self.codigo_original = None

        # Conexión a MySQL
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="dbtiendaletty"
        )
        self.cursor = self.conexion.cursor()

        self.crear_interfaz()
        self.crear_tabla_articulos()
        self.mostrar_nombres()

    def crear_tabla_articulos(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS articulos (
                    codigoBarras CHAR(13) PRIMARY KEY,
                    nombreArt VARCHAR(80),
                    marca VARCHAR(50),
                    cantidadAlmacen INT,
                    precioUnit DECIMAL(10,2),
                    caducidad DATETIME
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
        for i in range(10):
            self.root.grid_rowconfigure(i, weight=0)
        self.root.grid_rowconfigure(10, weight=1)

        # Título
        tk.Label(self.root, text="Artículos", font=("Impact", 20, "bold"), bg="#5bfcfe"
                 ).grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

        # Campos de entrada
        self.campos = {}
        campos_config = [
            ("Código Barras:", "codigoBarras", ""),
            ("Nombre:", "nombreArt", ""),
            ("Marca:", "marca", ""),
            ("Cantidad:", "cantidadAlmacen", ""),
            ("Precio Unitario:", "precioUnit", ""),
            ("Caducidad (YYYY-MM-DD):", "caducidad", "")
        ]

        for i, (texto, nombre, show_char) in enumerate(campos_config, start=1):
            tk.Label(self.root, text=texto, font=("Arial", 12), bg="#5bfcfe"
                     ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entry = tk.Entry(self.root, font=("Arial", 12), bg="#e6ffff")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.campos[nombre] = entry

        # Frame para botones principales
        frame_botones_principales = tk.Frame(self.root, bg="#5bfcfe")
        frame_botones_principales.grid(row=7, column=0, columnspan=3, pady=10)

        # Botones CRUD principales
        self.btn_crear = tk.Button(frame_botones_principales, text="Crear", bg="#A2E4B8",
                                   font=("Arial", 10), command=self.crear_articulo)
        self.btn_crear.grid(row=0, column=0, padx=5, ipadx=5, ipady=3)

        self.btn_leer = tk.Button(frame_botones_principales, text="Leer", bg="#9AD0F5",
                                  font=("Arial", 10), command=self.mostrar_detalles_articulo)
        self.btn_leer.grid(row=0, column=1, padx=5, ipadx=5, ipady=3)

        self.btn_editar = tk.Button(frame_botones_principales, text="Editar", bg="#FFE08A",
                                    font=("Arial", 10), command=self.preparar_edicion)
        self.btn_editar.grid(row=0, column=2, padx=5, ipadx=5, ipady=3)

        self.btn_borrar = tk.Button(frame_botones_principales, text="Borrar", bg="#F4A4A4",
                                    font=("Arial", 10), command=self.borrar_articulo)
        self.btn_borrar.grid(row=0, column=3, padx=5, ipadx=5, ipady=3)

        # Frame para botones secundarios (confirmar/cancelar/volver)
        self.frame_botones_secundarios = tk.Frame(self.root, bg="#5bfcfe")
        self.frame_botones_secundarios.grid(row=8, column=0, columnspan=3, pady=10)
        self.frame_botones_secundarios.grid_remove()  # Ocultar inicialmente

        self.btn_confirmar = tk.Button(self.frame_botones_secundarios, text="Confirmar", bg="#A2E4B8",
                                       font=("Arial", 10), command=self.confirmar_actualizacion)
        self.btn_confirmar.grid(row=0, column=0, padx=5, ipadx=5, ipady=3)

        self.btn_cancelar = tk.Button(self.frame_botones_secundarios, text="Cancelar", bg="#F4A4A4",
                                      font=("Arial", 10), command=self.cancelar_edicion)
        self.btn_cancelar.grid(row=0, column=1, padx=5, ipadx=5, ipady=3)

        self.btn_volver = tk.Button(self.frame_botones_secundarios, text="Volver a lista", bg="#9AD0F5",
                                    font=("Arial", 10), command=self.volver_a_lista)
        self.btn_volver.grid(row=0, column=2, padx=5, ipadx=5, ipady=3)

        # Frame para la tabla de artículos
        frame_tabla = tk.Frame(self.root)
        frame_tabla.grid(row=10, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))

        # Treeview para mostrar artículos
        self.tabla = ttk.Treeview(frame_tabla, columns=("Nombre","Marca"), show="headings")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Marca", text="Marca")
        self.tabla.column("Nombre", width=200)
        self.tabla.column("Marca", width=150)


        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Posicionamiento
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mostrar_nombres(self):
        """Muestra los nombres, marcas y precios de los artículos"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            self.cursor.execute("SELECT nombreArt, marca FROM articulos ORDER BY nombreArt")
            articulos = self.cursor.fetchall()

            for articulo in articulos:
                self.tabla.insert("", "end", values=(articulo[0], articulo[1]))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los artículos: {str(e)}")

    def mostrar_detalles_articulo(self):
        """Muestra todos los detalles del artículo seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un artículo primero")
            return

        nombre = self.tabla.item(seleccion[0])['values'][0]

        try:
            self.cursor.execute("SELECT * FROM articulos WHERE nombreArt = %s", (nombre,))
            articulo = self.cursor.fetchone()

            if articulo:
                # Configurar columnas para mostrar detalles
                self.tabla["columns"] = ("Código", "Nombre", "Marca", "Cantidad", "Precio", "Caducidad")

                # Configurar encabezados
                columnas = [
                    ("Código", 120),
                    ("Nombre", 200),
                    ("Marca", 150),
                    ("Cantidad", 80),
                    ("Precio", 100),
                    ("Caducidad", 120)
                ]

                for col, width in columnas:
                    self.tabla.heading(col, text=col)
                    self.tabla.column(col, width=width)

                # Limpiar tabla y mostrar solo este artículo
                for item in self.tabla.get_children():
                    self.tabla.delete(item)

                # Formatear precio y caducidad
                precio = f"${articulo[4]:.2f}" if articulo[4] else ""
                caducidad = articulo[5].strftime("%Y-%m-%d") if articulo[5] else ""

                self.tabla.insert("", "end", values=(
                    articulo[0], articulo[1], articulo[2], articulo[3], precio, caducidad
                ))
                self.articulo_seleccionado = articulo

                # Mostrar botón "Volver a lista"
                self.frame_botones_secundarios.grid()
                self.btn_volver.config(state=tk.NORMAL)
                self.btn_confirmar.config(state=tk.DISABLED)
                self.btn_cancelar.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Información", "No se encontraron detalles para este artículo")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles: {str(e)}")

    def preparar_edicion(self):
        """Prepara la interfaz para editar un artículo"""
        if not self.articulo_seleccionado:
            messagebox.showwarning("Advertencia", "Primero use 'Leer' en un artículo")
            return

        # Cargar datos en los campos
        self.limpiar_campos()
        self.campos['codigoBarras'].insert(0, self.articulo_seleccionado[0])
        self.campos['nombreArt'].insert(0, self.articulo_seleccionado[1])
        self.campos['marca'].insert(0, self.articulo_seleccionado[2] if self.articulo_seleccionado[2] else "")
        self.campos['cantidadAlmacen'].insert(0, str(self.articulo_seleccionado[3]) if self.articulo_seleccionado[
            3] else "")
        self.campos['precioUnit'].insert(0, str(self.articulo_seleccionado[4]) if self.articulo_seleccionado[4] else "")

        if self.articulo_seleccionado[5]:
            self.campos['caducidad'].delete(0, tk.END)
        self.campos['caducidad'].insert(0, self.articulo_seleccionado[5].strftime("%Y-%m-%d"))

        # Deshabilitar código de barras (es la clave primaria)
        self.campos['codigoBarras'].config(state='disabled')

        # Cambiar a modo edición
        self.modo_edicion = True
        self.codigo_original = self.articulo_seleccionado[0]

        # Mostrar botones de confirmación
        self.frame_botones_secundarios.grid()
        self.btn_confirmar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.NORMAL)
        self.btn_volver.config(state=tk.DISABLED)

        # Deshabilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.DISABLED)

    def confirmar_actualizacion(self):
        """Confirma la actualización del artículo"""
        datos = self.obtener_datos()

        # Validar campos obligatorios
        if not datos['nombreArt']:
            messagebox.showwarning("Error", "El nombre es un campo obligatorio")
            return

        try:
            # Convertir valores
            datos['cantidadAlmacen'] = int(datos['cantidadAlmacen']) if datos['cantidadAlmacen'] else 0
            datos['precioUnit'] = float(datos['precioUnit']) if datos['precioUnit'] else 0.0

            # Actualizar el artículo
            self.cursor.execute("""
                UPDATE articulos 
                SET nombreArt = %s, marca = %s, 
                    cantidadAlmacen = %s, precioUnit = %s, caducidad = %s
                WHERE codigoBarras = %s
            """, (
                datos['nombreArt'],
                datos['marca'],
                datos['cantidadAlmacen'],
                datos['precioUnit'],
                datos['caducidad'] if datos['caducidad'] else None,
                self.codigo_original
            ))

            self.conexion.commit()
            messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
            self.cancelar_edicion()
            self.volver_a_lista()
        except ValueError:
            messagebox.showerror("Error", "Cantidad y Precio deben ser números válidos")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el artículo: {str(e)}")

    def cancelar_edicion(self):
        """Cancela el modo de edición"""
        # Limpiar todos los campos, incluyendo el código de barras (aunque esté deshabilitado)
        for nombre, campo in self.campos.items():
            campo.config(state='normal')  # Habilitar temporalmente para limpiar
            campo.delete(0, tk.END)

        # Restaurar estado del campo código de barras
        self.campos['codigoBarras'].config(state='normal')

        self.modo_edicion = False
        self.codigo_original = None

        # Ocultar botones secundarios
        self.frame_botones_secundarios.grid_remove()

        # Habilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.NORMAL)

    def volver_a_lista(self):
        """Vuelve a mostrar la lista de nombres"""
        # Restablecer las columnas a solo "Nombre" (o las que quieras mostrar en la vista simple)
        self.tabla["columns"] = ("Nombre", "Marca")  # Nota la coma para que sea una tupla
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Marca", text="Marca")
        self.tabla.column("Nombre", width=200)
        self.tabla.column("Marca", width=150)

        # Mostrar solo los nombres
        self.mostrar_nombres()
        self.articulo_seleccionado = None
        self.frame_botones_secundarios.grid_remove()

        # Habilitar botones principales
        for btn in [self.btn_crear, self.btn_leer, self.btn_editar, self.btn_borrar]:
            btn.config(state=tk.NORMAL)

    def crear_articulo(self):
        """Crea un nuevo artículo en la base de datos"""
        datos = self.obtener_datos()

        # Validar campos obligatorios
        if not datos['codigoBarras'] or not datos['nombreArt']:
            messagebox.showwarning("Error", "Código de barras y nombre son campos obligatorios")
            return

        try:
            # Convertir cantidad a entero
            datos['cantidadAlmacen'] = int(datos['cantidadAlmacen']) if datos['cantidadAlmacen'] else 0
            # Convertir precio a float
            datos['precioUnit'] = float(datos['precioUnit']) if datos['precioUnit'] else 0.0

            self.cursor.execute("""
                INSERT INTO articulos (codigoBarras, nombreArt, marca, cantidadAlmacen, precioUnit, caducidad)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                datos['codigoBarras'],
                datos['nombreArt'],
                datos['marca'],
                datos['cantidadAlmacen'],
                datos['precioUnit'],
                datos['caducidad'] if datos['caducidad'] else None
            ))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Artículo creado correctamente")
            self.volver_a_lista()
            self.limpiar_campos()
        except ValueError:
            messagebox.showerror("Error", "Cantidad y Precio deben ser números válidos")
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "El código de barras ya existe")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el artículo: {str(e)}")

    def borrar_articulo(self):
        """Elimina un artículo de la base de datos"""
        if not self.articulo_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un artículo primero")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este artículo?"):
            try:
                self.cursor.execute("DELETE FROM articulos WHERE codigoBarras = %s", (self.articulo_seleccionado[0],))
                self.conexion.commit()
                messagebox.showinfo("Éxito", "Artículo eliminado correctamente")
                self.volver_a_lista()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el artículo: {str(e)}")

    def obtener_datos(self):
        """Obtiene los datos de los campos de entrada"""
        return {
            'codigoBarras': self.campos['codigoBarras'].get(),
            'nombreArt': self.campos['nombreArt'].get(),
            'marca': self.campos['marca'].get(),
            'cantidadAlmacen': self.campos['cantidadAlmacen'].get(),
            'precioUnit': self.campos['precioUnit'].get(),
            'caducidad': self.campos['caducidad'].get()
        }

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
    app = ArticulosApp(root)
    root.mainloop()