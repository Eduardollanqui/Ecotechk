from infraestructura.conexion import obtener_conexion

# Inserción de prueba
# al ejecutar la prueba se intentara volver a insetar la misma primary key(rut),
#  por lo que oracle bloqueara el duplicado como corresponde, para poder probar
#solo basta con cambiar los datos de isercion(nombre, rut) por otros que no estan en la base de datos
with obtener_conexion() as conn, conn.cursor() as cursor:
    cursor.execute(
        "INSERT INTO persona (rut, nombre) VALUES (:1, :2)",
        ("15000123-4", "Nelson Llanquileo"),
    )

# Lectura de prueba
with obtener_conexion() as conn, conn.cursor() as cursor:
    cursor.execute("SELECT rut, nombre FROM persona")
    filas = cursor.fetchall()
    for fila in filas:
        print(fila)