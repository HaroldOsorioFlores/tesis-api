from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_password_hash, get_user_by_email, verify_password
from app.db.db_connection import get_db
from app.models.dtos import ModelResponseDTO, RecommendationRequestDTO, RecommendationResponseDTO
from app.models.models import Producto, UserCreate
from app.util.util import calcular_tmb, calcular_calorias_totales, calcular_macronutrientes, get_combination_at_index
import numpy as np
from app.services.load_service import model_service


async def register_user(user: UserCreate, connection = Depends(get_db)):
    print(f"Intentando registrar usuario {user}")
    existing_user = await get_user_by_email(user.correo, connection)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    print(f"existing email: {existing_user}")
    hashed_password = get_password_hash(user.contrasenia)

    print(f"hashed_password {hashed_password}")
    
    cursor = connection.cursor()

    print(f"cursor XD: {cursor}")

    try:
        cursor.execute(
            "INSERT INTO usuarios (nombres, apellidos, correo, contrasenia) VALUES (%s, %s, %s, %s)",
            (user.nombres, user.apellidos, user.correo, hashed_password)
        )
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Error while creating user")
    finally:
        cursor.close()

    user_search = await get_user_by_email(user.correo, connection)

    print(f"Usuario creado: {user_search}")
    return user_search


async def login_for_access_token(form_data: OAuth2PasswordRequestForm, connection = Depends(get_db)):
    print(f"Intentando iniciar sesión con form_data: {form_data.username}")
    user = await get_user_by_email(form_data.username, connection)

    print(f"Usuario encontrado: {user}")

    if not user or not verify_password(form_data.password, user.contrasenia):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.correo}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_productos_db(correo: str ,connection = Depends(get_db)) :
    try:
        user = await get_user_by_email(correo, connection)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autorizado ",
                headers={"WWW-Authenticate": "Bearer"}
            )

        cursor = connection.cursor()

        query_get_productos = """
            SELECT id, nombre, proteinas,grasas, carbohidratos, estado FROM productos
        """

        cursor.execute(query_get_productos)

        data = cursor.fetchall()
   
        productos = [
            Producto(
                id=row[0],
                nombre=row[1],
                proteinas=row[2],
                grasas=row[3],
                carbohidratos=row[4],
                estado=row[5]
            ) for row in data
        ]

        return productos
    
    except Exception as error:
        print(f"Error: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los productos")

# controlador de recomendaciones esto se vincula con el endpoint
async def get_recommendations_db(data: RecommendationRequestDTO, correo: str, connection=Depends(get_db)):
    print(f"data_get_recomendations_db: {data}")
    tmb = calcular_tmb(data.peso, data.altura, data.edad, data.genero)
    calorias_totales = calcular_calorias_totales(tmb, data.nivel_actividad)
    macronutrientes = calcular_macronutrientes(calorias_totales)

    necesidades_usuario = np.array(macronutrientes)
    print(f"necesidades_usuario: {necesidades_usuario}")

    distancias, indices = model_service.knn_loaded.kneighbors([necesidades_usuario])
    print(f"indices: {indices}")

    recomendaciones = []
    for i in range(10):
        combinacion_recomendada = model_service.combinaciones_productos[indices.flatten()[i] + 1]
        indices_recomendados = get_combination_at_index(len(model_service.nombres_productos), indices.flatten()[i] + 1)
        productos_recomendados = [model_service.nombres_productos[j] for j in indices_recomendados]
        recomendaciones.append({
            "combinacion_recomendada": combinacion_recomendada.tolist(),
            "productos_recomendados": productos_recomendados,
            "distancia": distancias.flatten()[i]
        })
    print(f"recomendaciones: {recomendaciones}")

    productos_db = await get_productos_db(correo, connection)
    print(f"productos_db: {productos_db}")
    productos_map = {producto.nombre: producto for producto in productos_db}
    print(f"productos_map: {productos_map}")

    recomendaciones_finales = []
    for recomendacion in recomendaciones:
        productos_recomendados = [productos_map[nombre] for nombre in recomendacion["productos_recomendados"]]
        recomendaciones_finales.append(RecommendationResponseDTO(
            combinacion_recomendada=recomendacion["combinacion_recomendada"],
            productos_recomendados=[Producto(**producto.__dict__) for producto in productos_recomendados],
            distancia=recomendacion["distancia"]
        ))
    print(f"recomendaciones_finales: {recomendaciones_finales}")

    return ModelResponseDTO(status_code=200, detail="Recomendaciones obtenidas exitosamente", data=recomendaciones_finales)