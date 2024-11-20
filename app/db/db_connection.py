import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()
async def create_connection():
    try:
        print(f"prueba: {os.getenv('DB_HOST')}")

        connection = await aiomysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASSWORD", "admin"),
            db=os.getenv("DB_NAME", "recfoodcato"),
            port=int(os.getenv("DB_PORT", "3308"))
        )
        print("Conexión exitosa")
        return connection
    except aiomysql.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

async def get_db():
    connection = await create_connection()
    try:
        yield connection  # Usar yield para devolver la conexión
    finally:
        connection.close()  # Cierra la conexión
