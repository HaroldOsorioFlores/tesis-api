from typing import Annotated, List
from fastapi import FastAPI, status
from fastapi_pagination import Page, add_pagination, paginate
from app.controllers.controllers import get_productos_db, get_recommendations_db, login_for_access_token, obtener_historial_recomendaciones_y_productos, register_user
from app.db.db_connection import get_db
from app.models.dtos import ErrorResponseDTO, ModelResponseDTO, RecommendationRequestDTO
from app.models.models import  HistorialRecomendacionResponse, Token, UserCreate,UserInDB
from fastapi import Depends, FastAPI
from fastapi.security import  OAuth2PasswordRequestForm
from app.auth import  get_current_active_user
from fastapi.middleware.cors import CORSMiddleware
from .services.load_service import model_service

app = FastAPI()
add_pagination(app) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
async def startup_event():
    print("iniciando carga del modelo")
    await model_service.load_model_and_data()
    print(f"Modelo cargado al inicio de la app: {model_service.knn_loaded}")


@app.on_event("shutdown")
async def shutdown_event():
    print("Aplicación terminada")

@app.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de FastAPI!"}

@app.post("/register", response_model=UserInDB)
async def register(user: UserCreate, db=Depends(get_db)):
    print(f"controller usuario creado: {user}")
    return await register_user(user, db)


@app.post("/login", response_model=Token, responses={401: {"model": ErrorResponseDTO}})
async def login(form_data: OAuth2PasswordRequestForm= Depends(), db=Depends(get_db)):
    return await login_for_access_token(form_data, db)


@app.get("/productos", response_model=ModelResponseDTO, responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponseDTO}})
async def get_productos(current_user: Annotated[ModelResponseDTO, Depends(get_current_active_user)], connection=Depends(get_db)):
    productos = await get_productos_db(current_user.data.correo, connection)

    return ModelResponseDTO(status_code=200, detail="Productos obtenidos exitosamente", data=productos)

@app.post("/recommendations", response_model=ModelResponseDTO, responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponseDTO}})
async def get_recommendations(data: RecommendationRequestDTO, current_user: Annotated[ModelResponseDTO, Depends(get_current_active_user)], connection=Depends(get_db)):
    print(f"recomendaciones main: {data}")
    recomendaciones_finales = await get_recommendations_db(data, current_user.data.correo, connection)
    return recomendaciones_finales

@app.get("/history-recomendations", response_model=Page[HistorialRecomendacionResponse])
async def get_recomendaciones(
    current_user: Annotated[ModelResponseDTO, Depends(get_current_active_user)],
    connection=Depends(get_db)
):
    recomendaciones = await obtener_historial_recomendaciones_y_productos(current_user.data.correo, connection)
    return paginate(recomendaciones)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
