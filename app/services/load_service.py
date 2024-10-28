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


        print(f"Modelo cargado desde: {file_path_model}")

        file_path_productos = os.path.join(current_dir, '../data/productos.csv')
        self.nombres_productos = pd.read_csv(file_path_productos, sep=';')['Producto'].values

        file_path_combinaciones = os.path.join(current_dir, '../data/combinaciones_productos.csv')
        self.combinaciones_productos = np.array(pd.read_csv(file_path_combinaciones, sep=';'))

        print("Modelo y datos cargados correctamente")

model_service = ModelService()