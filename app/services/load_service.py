import joblib
import os
import pandas as pd
import numpy as np

# servicio de carga del modelo de machine learning
class ModelService:
    def __init__(self):
        self.knn_loaded = None
        self.nombres_productos = None
        self.combinaciones_productos = None

    async def load_model_and_data(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        file_path_model = os.path.join(current_dir, '../data/modelo_knn.joblib')
        print("Iniciando carga del modelo...")
        self.knn_loaded = joblib.load(file_path_model)
        print(f"Modelo cargado: {self.knn_loaded}")


        # Cargar el archivo CSV
        file_path_csv = os.path.join(current_dir, '../data/combinaciones_productos.csv')
        print("Iniciando carga del archivo CSV...")
        df_cp = pd.read_csv(file_path_csv, sep=';')
        self.combinaciones_productos = np.array(df_cp)
        print(f"Archivo CSV cargado: {self.combinaciones_productos}")

        print("Modelo y datos cargados correctamente")

   

model_service = ModelService()