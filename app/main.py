from typing import Annotated
from fastapi import FastAPI, status
from app.controllers.controllers import get_productos_db, get_recommendations_db, login_for_access_token, register_user
from app.db.db_connection import get_db
from app.models.dtos import ErrorResponseDTO, ModelResponseDTO, RecommendationRequestDTO
from app.models.models import Token, UserCreate,UserInDB
from fastapi import Depends, FastAPI
from fastapi.security import  OAuth2PasswordRequestForm
from app.auth import  get_current_active_user
from fastapi.middleware.cors import CORSMiddleware
from .services.load_service import model_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
async def startup_event():
    await model_service.load_model_and_data()
    print(f"Modelo cargado al inicio de la app: {model_service.knn_loaded}")
    # Crear un archivo de señal para indicar que el modelo se ha cargado


@app.on_event("shutdown")
async def shutdown_event():
    print("Aplicación terminada")

@app.post("/register", response_model=UserInDB)
async def register(user: UserCreate, db=Depends(get_db)):
    print(f"controller usuario creado: {user}")
    return await register_user(user, db)

# @app.post("/prueba", response_description="Buen dia")
# async def prueba(mensaje:str):
#     return {"mensaje":mensaje}

@app.post("/login", response_model=Token, responses={401: {"model": ErrorResponseDTO}})
async def login(form_data: OAuth2PasswordRequestForm= Depends(), db=Depends(get_db)):
    return await login_for_access_token(form_data, db)

# @app.get("/users/me", response_model=ModelResponseDTO)
# async def read_users_me(current_user: Annotated[ModelResponseDTO, Depends(get_current_active_user)]):
#     print(f"currect_user {current_user}")
#     return current_user


@app.get("/productos", response_model=ModelResponseDTO, responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponseDTO}})
async def get_productos(current_user: Annotated[ModelResponseDTO, Depends(get_current_active_user)], connection=Depends(get_db)):
    productos = await get_productos_db(current_user.data.correo, connection)

    return ModelResponseDTO(status_code=200, detail="Productos obtenidos exitosamente", data=productos)

# endpoint de recomendacion
@app.post("/recommendations", response_model=ModelResponseDTO, responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponseDTO}})
async def get_recommendations(data: RecommendationRequestDTO, current_user: Annotated[ModelResponseDTO, Depends(get_current_active_user)], connection=Depends(get_db)):
    print(f"recomendaciones main: {data}")
    recomendaciones_finales = await get_recommendations_db(data, current_user.data.correo, connection)
    return recomendaciones_finales

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
