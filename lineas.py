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
        print("Error al conectar a MySQL", e)
        return None


def crear_tabla_lineainv(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lineainv (
            clavein CHAR(10) PRIMARY KEY,
            nombre VARCHAR(250) NOT NULL
        )
    """)
    print("Tabla lineainv creada correctamente.")


def insertar_lineainv(cursor, clave, nombre):
    try:
        cursor.execute("INSERT INTO lineainv (clavein, nombre) VALUES (%s, %s)", (clave, nombre))
        print("Registro insertado correctamente.")
    except Error as e:
        print(f"Error al insertar registro: {e}")


def leer_lineainv(cursor):
    cursor.execute("SELECT * FROM lineainv")
    print("\nLista de Líneas de Investigación:")
    for fila in cursor.fetchall():
        print(f"Clave: {fila[0]}, Nombre: {fila[1]}")


def actualizar_lineainv(cursor, clave, nuevo_nombre):
    cursor.execute("UPDATE lineainv SET nombre = %s WHERE clavein = %s", (nuevo_nombre, clave))
    print("Registro actualizado correctamente.")


def eliminar_lineainv(cursor, clave):
    cursor.execute("DELETE FROM lineainv WHERE clavein = %s", (clave,))
    print("Registro eliminado correctamente.")


def main():
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        crear_tabla_lineainv(cursor)

        try:
            insertar_lineainv(cursor, 'INV001', 'Inteligencia Artificial')
            conexion.commit()
        except:
            print("El registro con clave 'INV001' ya existe.")

        leer_lineainv(cursor)

        actualizar_lineainv(cursor, 'INV001', 'Machine Learning')
        conexion.commit()
        leer_lineainv(cursor)

        eliminar_lineainv(cursor, 'INV001')
        conexion.commit()
        leer_lineainv(cursor)

        cursor.close()
        conexion.close()


if __name__ == "__main__":
    main()
