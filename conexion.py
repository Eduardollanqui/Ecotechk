import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

def obtener_conexion():
    usuario = os.getenv("DB_USUARIO")
    contrasena = os.getenv("DB_CONTRASENA")
    dsn = os.getenv("DB_DSN")

    conn =oracledb.connect(user=usuario, password=contrasena, dsn=dsn)

    return conn

