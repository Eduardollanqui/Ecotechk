import os
from dotenv import load_dotenv

load_dotenv()

ruta_db = os.getenv("DB_NOMBRE")
print("la ruta de la basae de datos es:", ruta_db)
