import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('.env')

def get_connection():
    """
    Crea y retorna una conexión a PostgreSQL.
    Usamos las credenciales del archivo .env para no
    escribir contraseñas directamente en el código.
    """
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return connection


def test_connection():
    """
    Prueba que la conexión funcione correctamente.
    Útil para verificar antes de ejecutar el ETL.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"✅ Conexión exitosa: {version[0]}")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


if __name__ == "__main__":
    test_connection()