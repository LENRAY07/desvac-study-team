import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mysql',
            database='dbtaller'
        )
        if conexion.is_connected():
            print("Conexión exitosa a MySQL")
        return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def crear_tabla_tipoProyecto(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tipoProyecto (
            tipo CHAR(3),
            nombre VARCHAR(550) NOT NULL,
            PRIMARY KEY(tipo, nombre)
        )
    """)
    print("Tabla Tipo Proyecto creada correctamente.")

def insertar_tipoProy(cursor, conexion):
    tipo = input("Ingresa el tipo del proyecto: ")
    nombre = input("Ingresa el nombre del proyecto: ")
    try:
        cursor.execute("INSERT INTO tipoProyecto (tipo, nombre) VALUES (%s, %s)", (tipo, nombre))
        conexion.commit()
        print("Registro insertado correctamente.")
    except Error as e:
        print(f"Error al insertar registro: {e}")

def leer_tipoProy(cursor):
    cursor.execute("SELECT * FROM tipoProyecto")
    print("\nLista de Tipos de Proyectos:")
    for fila in cursor.fetchall():
        print(f"Tipo: {fila[0]}, Nombre: {fila[1]}")

def actualizar_tipoProy(cursor, conexion):
    tipo = input("Ingresa el tipo del proyecto a actualizar: ")
    nombre_actual = input("Ingresa el nombre actual del proyecto: ")
    nuevo_nombre = input("Ingresa el nuevo nombre del proyecto: ")
    try:
        cursor.execute("UPDATE tipoProyecto SET nombre = %s WHERE tipo = %s AND nombre = %s",
                       (nuevo_nombre, tipo, nombre_actual))
        conexion.commit()
        if cursor.rowcount > 0:
            print("Registro actualizado correctamente.")
        else:
            print("No se encontró el registro a actualizar.")
    except Error as e:
        print(f"Error al actualizar registro: {e}")

def eliminar_tipoProy(cursor, conexion):
    tipo = input("Ingresa el tipo del proyecto a eliminar: ")
    nombre = input("Ingresa el nombre del proyecto a eliminar: ")
    try:
        cursor.execute("DELETE FROM tipoProyecto WHERE tipo = %s AND nombre = %s", (tipo, nombre))
        conexion.commit()
        if cursor.rowcount > 0:
            print("Registro eliminado correctamente.")
        else:
            print("No se encontró el registro a eliminar.")
    except Error as e:
        print(f"Error al eliminar registro: {e}")

def main():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        crear_tabla_tipoProyecto(cursor)
        while True:
            print("\nMenú de Opciones:")
            print("1. Insertar el Tipo de Proyecto")
            print("2. Leer los Tipos de Proyecto")
            print("3. Actualizar el Tipo de Proyecto")
            print("4. Eliminar el Tipo de Proyecto")
            print("5. Salir")
            opcion = input("Selecciona una opción: ")
            if opcion == '1':
                insertar_tipoProy(cursor, conexion)
            elif opcion == '2':
                leer_tipoProy(cursor)
            elif opcion == '3':
                actualizar_tipoProy(cursor, conexion)
            elif opcion == '4':
                eliminar_tipoProy(cursor, conexion)
            elif opcion == '5':
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
        cursor.close()
        conexion.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    main()
