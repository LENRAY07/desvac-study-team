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


def insertar_tipoProy(cursor, conexion, tipo, nombre):
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


def actualizar_tipoProy(cursor, conexion, tipo, nombre_actual, nuevo_nombre):
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


def eliminar_tipoProy(cursor, conexion, tipo, nombre):
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

        insertar_tipoProy(cursor, conexion, 'DT', 'Diseño de infraestructura de redes y comunicaciones para el IEPC')
        leer_tipoProy(cursor)

        actualizar_tipoProy(cursor, conexion, 'DT', 'Diseño de infraestructura de redes y comunicaciones para el IEPC',
                            'PersonalFitnes: Aplicación web para rutinas de ejercicios personalizadas')
        leer_tipoProy(cursor)

        eliminar_tipoProy(cursor, conexion, 'DT', 'PersonalFitnes: Aplicación web para rutinas de ejercicios personalizadas')
        leer_tipoProy(cursor)

        cursor.close()
        conexion.close()


if __name__ == "__main__":
    main()

