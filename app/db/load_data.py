import pandas as pd
from db_connection import create_connection
import os

def load_data_to_db():
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
        connection = create_connection()
        cursor = connection.cursor()

        for index, row in df.iterrows():
            insert_query = """
            INSERT INTO productos (nombre, proteinas, grasas, carbohidratos)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (row['Producto'], row['Proteinas'], row['Grasas'], row['Carbohidratos']))

        connection.commit()
        print("Datos insertados exitosamente.")

    except Exception as e:
        print(f"Error al insertar datos: {e}")

    finally:
        cursor.close()
        connection.close()

load_data_to_db()