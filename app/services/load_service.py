import joblib
import os
import pandas as pd
import numpy as np
import boto3


# servicio de carga del modelo de machine learning
class ModelService:
    def __init__(self):
        self.knn_loaded = None
        self.nombres_productos = None
        self.combinaciones_productos = None
        self.s3 = boto3.client('s3')

    async def load_model_and_data(self):
        await self.download_file('mi-bucket-de-modelos', 'modelo_knn.joblib', '/tmp/modelo_knn.joblib')
        await self.download_file('mi-bucket-de-modelos', 'combinaciones_productos.csv', '/tmp/combinaciones_productos.csv')

        print("Iniciando carga del modelo...")
        self.knn_loaded = joblib.load('/tmp/modelo_knn.joblib')
        print(f"Modelo cargado: {self.knn_loaded}")

        print("Iniciando carga del archivo CSV...")
        df_cp = pd.read_csv('/tmp/combinaciones_productos.csv', sep=';')
        self.combinaciones_productos = np.array(df_cp)
        print(f"Archivo CSV cargado: {self.combinaciones_productos}")

        print("Modelo y datos cargados correctamente")

    async def download_file(self, bucket_name, object_key, file_path):
        if not os.path.exists(file_path):
            print(f"Descargando {object_key} desde S3...")
            self.s3.download_file(bucket_name, object_key, file_path)
            print(f"Archivo {object_key} descargado correctamente")
   

model_service = ModelService()