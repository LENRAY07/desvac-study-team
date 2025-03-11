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
            print("\nConexión exitosa a MySQL")
        return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def crear_tabla_lineainv(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lineainv (
            clavein CHAR(10) PRIMARY KEY,
            nombre VARCHAR(250) NOT NULL
        )
    """)
    print("Tabla lineainv verificada correctamente.")

def insertar_lineainv(cursor, conexion):
    clave = input("\nIngrese la clave de la Línea de Investigación: ")
    nombre = input("Ingrese el nombre de la Línea de Investigación: ")
    try:
        cursor.execute("INSERT INTO lineainv (clavein, nombre) VALUES (%s, %s)", (clave, nombre))
        conexion.commit()
        print(f"Línea de investigación '{nombre}' insertada correctamente.")
    except Error as e:
        print(f"Error al insertar línea de investigación: {e}")

def leer_lineainv(cursor):
    cursor.execute("SELECT * FROM lineainv")
    lineas = cursor.fetchall()
    if lineas:
        print("\nLista de Líneas de Investigación:")
        for linea in lineas:
            print(f"Clave: {linea[0]}, Nombre: {linea[1]}")
    else:
        print("No hay líneas de investigación registradas.")

def actualizar_lineainv(cursor, conexion):
    clave = input("\nIngrese la clave de la Línea de Investigación a actualizar: ")
    nuevo_nombre = input("Ingrese el nuevo nombre: ")
    try:
        cursor.execute("UPDATE lineainv SET nombre = %s WHERE clavein = %s", (nuevo_nombre, clave))
        conexion.commit()
        if cursor.rowcount > 0:
            print(f"Línea con clave '{clave}' actualizada a '{nuevo_nombre}'.")
        else:
            print("No se encontró la línea de investigación a actualizar.")
    except Error as e:
        print(f"Error al actualizar línea de investigación: {e}")

def eliminar_lineainv(cursor, conexion):
    clave = input("\nIngrese la clave de la Línea de Investigación a eliminar: ")
    try:
        cursor.execute("DELETE FROM lineainv WHERE clavein = %s", (clave,))
        conexion.commit()
        if cursor.rowcount > 0:
            print(f"Línea con clave '{clave}' eliminada correctamente.")
        else:
            print("No se encontró la línea de investigación a eliminar.")
    except Error as e:
        print(f"Error al eliminar línea de investigación: {e}")

def main():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        crear_tabla_lineainv(cursor)

        while True:
            print("\n--- MENÚ CRUD: LÍNEAS DE INVESTIGACIÓN ---")
            print("1. Insertar la Línea de Investigación")
            print("2. Mostrar la Líneas de Investigación")
            print("3. Actualizar la Línea de Investigación")
            print("4. Eliminar la Línea de Investigación")
            print("5. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                insertar_lineainv(cursor, conexion)
            elif opcion == '2':
                leer_lineainv(cursor)
            elif opcion == '3':
                actualizar_lineainv(cursor, conexion)
            elif opcion == '4':
                eliminar_lineainv(cursor, conexion)
            elif opcion == '5':
                print("Saliendo del programa...")
                break
            else:
                print("Opción no válida. Intente de nuevo.")

        cursor.close()
        conexion.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    main()

