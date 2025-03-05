import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="<mysql>",
    database="dbtaller"
)


if conexion.is_connected():
    print("Conexión exitosa")

    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM nombre_de_tabla")  # Cambia 'nombre_de_tabla' por el nombre real
    registros = cursor.fetchall()
    print("\nDatos en la tabla:")
    for fila in registros:
        print(fila)

    cursor.execute("INSERT INTO nombre_de_tabla (columna1, columna2) VALUES (%s, %s)", ("valor1", "valor2"))
    conexion.commit()  # Guardar cambios
    print("\nNuevo dato insertado.")


    cursor.execute("UPDATE nombre_de_tabla SET columna1 = %s WHERE columna2 = %s", ("nuevo_valor", "valor2"))
    conexion.commit()
    print("\nDato actualizado.")

    cursor.close()
    conexion.close()
    print("\nConexión cerrada.")


