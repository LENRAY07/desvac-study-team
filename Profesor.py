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


def crear_tabla_profesor(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profesor (
            idprofesor INT AUTO_INCREMENT PRIMARY KEY,
            nombreProf VARCHAR(200) NOT NULL
        )
    """)
    print("Tabla profesor verificada correctamente.")


def insertar_profesor(cursor, conexion):
    nombreProf = input("\nIngrese el nombre del profesor: ")
    try:
        cursor.execute("INSERT INTO profesor (nombreProf) VALUES (%s)", (nombreProf,))
        conexion.commit()
        print(f"Profesor '{nombreProf}' insertado correctamente.")
    except Error as e:
        print(f"Error al insertar profesor: {e}")


def leer_profesores(cursor):
    cursor.execute("SELECT * FROM profesor")
    profesores = cursor.fetchall()
    if profesores:
        print("\nLista de Profesores:")
        for profesor in profesores:
            print(f"ID: {profesor[0]}, Nombre: {profesor[1]}")
    else:
        print("No hay profesores registrados.")


def actualizar_profesor(cursor, conexion):
    idprofesor = input("\nIngrese el ID del profesor que desea actualizar: ")
    nuevo_nombre = input("Ingrese el nuevo nombre: ")
    try:
        cursor.execute("UPDATE profesor SET nombreProf = %s WHERE idprofesor = %s",
                       (nuevo_nombre, idprofesor))
        conexion.commit()
        if cursor.rowcount > 0:
            print(f"Profesor con ID {idprofesor} actualizado a '{nuevo_nombre}'.")
        else:
            print("No se encontró el profesor a actualizar.")
    except Error as e:
        print(f"Error al actualizar profesor: {e}")

def eliminar_profesor(cursor, conexion):
    idprofesor = input("\nIngrese el ID del profesor que desea eliminar: ")
    try:
        cursor.execute("DELETE FROM profesor WHERE idprofesor = %s", (idprofesor,))
        conexion.commit()
        if cursor.rowcount > 0:
            print(f"Profesor con ID {idprofesor} eliminado correctamente.")
        else:
            print("No se encontró el profesor a eliminar.")
    except Error as e:
        print(f"Error al eliminar profesor: {e}")


def main():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        crear_tabla_profesor(cursor)

        while True:
            print("\n--- MENÚ CRUD ---")
            print("1. Insertar Profesor")
            print("2. Mostrar Profesores")
            print("3. Actualizar Profesor")
            print("4. Eliminar Profesor")
            print("5. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                insertar_profesor(cursor, conexion)
            elif opcion == '2':
                leer_profesores(cursor)
            elif opcion == '3':
                actualizar_profesor(cursor, conexion)
            elif opcion == '4':
                eliminar_profesor(cursor, conexion)
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
