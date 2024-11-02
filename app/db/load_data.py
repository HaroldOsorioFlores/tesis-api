import asyncio
import pandas as pd
from db_connection import create_connection
import os

async def load_data_to_db():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, '../data/productos.csv')
        df = pd.read_csv(file_path, sep=";")
        
    except FileNotFoundError:
        print("Error: El archivo productos.csv no se encontró.")
        return  
    except pd.errors.EmptyDataError:
        print("Error: El archivo productos.csv está vacío.")
        return
    except pd.errors.ParserError:
        print("Error: Hubo un problema al analizar el archivo productos.csv.")
        return

    try:
        connection = await create_connection()
        cursor = await connection.cursor()

        for index, row in df.iterrows():
            insert_query = """
            INSERT INTO productos (nombre, proteinas, grasas, carbohidratos)
            VALUES (%s, %s, %s, %s)
            """
            await cursor.execute(insert_query, (row['Producto'], row['Proteinas'], row['Grasas'], row['Carbohidratos']))

        await connection.commit()
        print("Datos insertados exitosamente.")

    except Exception as e:
        print(f"Error al insertar datos: {e}")

    finally:
        await cursor.close()
        connection.close()

asyncio.run(load_data_to_db())

