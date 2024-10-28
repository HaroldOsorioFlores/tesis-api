import mysql.connector
from mysql.connector import Error
import os

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),  
            user=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASSWORD", "admin"),
            database=os.getenv("DB_NAME", "recfoodcato"),
            port=os.getenv("DB_PORT", "3308")
        )
        if connection.is_connected():
            print("Conexión exitosa")
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    
def get_db():
    connection = create_connection()
    try:
        yield connection  # Usar yield para devolver la conexión
    finally:
        connection.close()  # Asegúrate de cerrar la conexión

