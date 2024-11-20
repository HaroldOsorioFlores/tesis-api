from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Tiempo de espera entre tareas (en segundos)

    @task
    def login_and_get_recommendations(self):
        # Simula un inicio de sesión
        login_data = {
            "grant_type": "password",
            "username": "harold@gmail.com",
            "password": "harold",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        login_response = self.client.post("/login", data=login_data)
        
        # Verifica si el inicio de sesión fue exitoso
        if login_response.status_code == 200:
            # Extrae el token de autenticación
            auth_token = login_response.json().get("access_token")
            
            if auth_token:
                # Datos para la recomendación
                recommendation_data = {
                    "peso": 66.2,
                    "altura": 168,
                    "edad": 22,
                    "genero": 0,
                    "nivel_actividad": 0
                }
                
                # Simula la solicitud de recomendaciones con el token de autenticación
                headers = {"Authorization": f"Bearer {auth_token}"}
                recommendation_response = self.client.post("/recommendations", json=recommendation_data, headers=headers)
                
                if recommendation_response.status_code != 200:
                    print(f"Error en la solicitud de recomendaciones: {recommendation_response.status_code} - {recommendation_response.text}")
            else:
                print("No se pudo obtener el token de autenticación")
        else:
            print(f"Error en el inicio de sesión: {login_response.status_code} - {login_response.text}")

    @task
    def view_history(self):
        # Simula la visualización del historial de recomendaciones
        login_data = {
            "grant_type": "password",
            "username": "harold@gmail.com",
            "password": "harold",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        login_response = self.client.post("/login", data=login_data)
        
        # Verifica si el inicio de sesión fue exitoso
        if login_response.status_code == 200:
            # Extrae el token de autenticación
            auth_token = login_response.json().get("access_token")
            
            if auth_token:
                # Simula la solicitud para ver el historial con el token de autenticación
                headers = {"Authorization": f"Bearer {auth_token}"}
                history_response = self.client.get("/history-recomendations", headers=headers)
                
                if history_response.status_code != 200:
                    print(f"Error en la solicitud del historial: {history_response.status_code} - {history_response.text}")
            else:
                print("No se pudo obtener el token de autenticación")
        else:
            print(f"Error en el inicio de sesión: {login_response.status_code} - {login_response.text}")