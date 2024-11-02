from datetime import timedelta
import json
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_password_hash, get_user_by_email, verify_password
from app.db.db_connection import get_db
from app.models.dtos import ModelResponseDTO, RecommendationRequestDTO, RecommendationResponseDTO
from app.models.models import Producto, UserCreate
from app.util.util import calcular_tmb, calcular_calorias_totales, calcular_macronutrientes, get_combination_at_index
import numpy as np
from app.services.load_service import model_service


async def register_user(user: UserCreate, connection=Depends(get_db)):
    print(f"Intentando registrar usuario {user}")
    existing_user = await get_user_by_email(user.correo, connection)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    hashed_password = get_password_hash(user.contrasenia)
    
    print(f"hashed_password {hashed_password}")

    async with connection.cursor() as cursor:
        try:
            await cursor.execute(
                "INSERT INTO usuarios (nombres, apellidos, correo, contrasenia) VALUES (%s, %s, %s, %s)",
                (user.nombres, user.apellidos, user.correo, hashed_password)
            )
            await connection.commit()
        except Exception as e:
            await connection.rollback()
            raise HTTPException(status_code=500, detail="Error while creating user")

    user_search = await get_user_by_email(user.correo, connection)
    print(f"Usuario creado: {user_search}")
    return user_search


async def login_for_access_token(form_data: OAuth2PasswordRequestForm, connection=Depends(get_db)):
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

async def get_productos_db(correo: str, connection=Depends(get_db)):
    try:
        user = await get_user_by_email(correo, connection)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autorizado",
                headers={"WWW-Authenticate": "Bearer"}
            )

        async with connection.cursor() as cursor:
            query_get_productos = """
                SELECT id, nombre, proteinas, grasas, carbohidratos, estado FROM productos
            """

            await cursor.execute(query_get_productos)
            data = await cursor.fetchall()
       
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

async def obtener_producto_por_nombre(nombre: str, connection) -> Optional[Producto]:
    async with connection.cursor() as cursor:  
        await cursor.execute(
            "SELECT id, nombre, proteinas, grasas, carbohidratos, estado FROM productos WHERE nombre = %s",
            (nombre,)
        )
        producto_data = await cursor.fetchone()
        
        if producto_data:
            return Producto(
                id=producto_data[0],
                nombre=producto_data[1],
                proteinas=producto_data[2],
                grasas=producto_data[3],
                carbohidratos=producto_data[4],
                estado=producto_data[5]
            )
    
    return None

async def get_recommendations_db(data: RecommendationRequestDTO, correo: str, connection=Depends(get_db)):
    try:
        # Verificar usuario por correo
        user = await get_user_by_email(correo, connection)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autorizado",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Cálculos de TMB, calorías y macronutrientes
        tmb = calcular_tmb(data.peso, data.altura, data.edad, data.genero)
        calorias_totales = calcular_calorias_totales(tmb, data.nivel_actividad)
        macronutrientes = calcular_macronutrientes(calorias_totales)
        
        necesidades_usuario = np.array(macronutrientes)
        print(f"necesidades_usuario: {necesidades_usuario}")

        # Obtener los índices recomendados del modelo ML
        distancias, indices = model_service.knn_loaded.kneighbors([necesidades_usuario])
        print(f"indices: {indices}")

        # Crear una nueva recomendación en la tabla recomendaciones
        async with connection.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO recomendaciones (usuario_id, peso, talla, edad)
                VALUES (%s, %s, %s, %s)
                """,
                (user.id, data.peso, data.altura, data.edad)
            )
            recomendacion_id = cursor.lastrowid

            recomendaciones = []
            for i in range(10):
                indices_recomendados = get_combination_at_index(len(model_service.nombres_productos), indices.flatten()[i] + 1)
                productos_recomendados = []
                producto_ids = []

                for j in indices_recomendados:
                    nombre_producto = model_service.nombres_productos[j]

                    # Obtener el producto completo en lugar de solo el nombre
                    producto = await obtener_producto_por_nombre(nombre_producto, connection)

                    if producto:  # Asegurarse de que el producto existe
                        productos_recomendados.append(producto)  # Agregar el producto como instancia de Producto
                        producto_ids.append(producto.id)  # Agregar el id del producto a la lista

                # Agregar recomendaciones solo si hay productos recomendados
                if productos_recomendados:
                    recomendaciones.append({
                        "combinacion_recomendada": indices_recomendados,
                        "productos_recomendados": productos_recomendados,
                        "distancia": distancias.flatten()[i]
                    })

                    # Insertar en la tabla intermedia recomendacion_producto
                    await cursor.execute(
                        """
                        INSERT INTO recomendacion_producto (recomendacion_id, producto_ids)
                        VALUES (%s, %s)
                        """,
                        (recomendacion_id, json.dumps(producto_ids))  # Usar el id del producto
                    )
            
            await connection.commit()

            # Estructurar la respuesta
            recomendaciones_finales = [
                RecommendationResponseDTO(
                    combinacion_recomendada=recomendacion["combinacion_recomendada"],
                    productos_recomendados=recomendacion["productos_recomendados"],  # Esto ahora tiene instancias de Producto
                    distancia=recomendacion["distancia"]
                )
                for recomendacion in recomendaciones
            ]

            return ModelResponseDTO(status_code=200, detail="Recomendaciones obtenidas exitosamente", data=recomendaciones_finales)

    except Exception as error:
        print(f"Error: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener las recomendaciones")

async def obtener_historial_recomendaciones_y_productos(correo: str, connection):
    # Verificar si el usuario existe
    try:
        # Verificar usuario por correo
        user = await get_user_by_email(correo, connection)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autorizado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        async with connection.cursor() as cursor:  # No usar aiomysql.DictCursor
            usuario_id = user.id

            # Obtener las recomendaciones y productos asociados
            await cursor.execute("""
                SELECT 
                    r.id AS recomendacion_id,
                    r.usuario_id,
                    r.peso,
                    r.talla,
                    r.edad,
                    r.f_recomendacion,
                    JSON_EXTRACT(rp.producto_ids, '$[*]') AS producto_ids
                FROM 
                    recomendaciones r
                JOIN 
                    recomendacion_producto rp ON r.id = rp.recomendacion_id
                WHERE 
                    r.usuario_id = %s
            """, (usuario_id,))
            results = await cursor.fetchall()

            recomendaciones = {}
            for row in results:
                recomendacion_id = row[0]  # Acceder por índice
                if recomendacion_id not in recomendaciones:
                    recomendaciones[recomendacion_id] = {
                        'id': recomendacion_id,
                        'usuario_id': row[1],  # Acceder por índice
                        'peso': row[2],  # Acceder por índice
                        'talla': row[3],  # Acceder por índice
                        'edad': row[4],  # Acceder por índice
                        'f_recomendacion': row[5].isoformat(),  # Acceder por índice
                        'productos': []
                    }
                producto_ids = json.loads(row[6])  # Acceder por índice y convertir a lista
                productos = []
                for producto_id in producto_ids:
                    await cursor.execute("""
                        SELECT 
                            id, nombre, proteinas, grasas, carbohidratos, estado
                        FROM 
                            productos
                        WHERE 
                            id = %s
                    """, (producto_id,))
                    producto_result = await cursor.fetchone()
                    if producto_result:
                        productos.append({
                            'id': producto_result[0],  # Acceder por índice
                            'nombre': producto_result[1],  # Acceder por índice
                            'proteinas': producto_result[2],  # Acceder por índice
                            'grasas': producto_result[3],  # Acceder por índice
                            'carbohidratos': producto_result[4],  # Acceder por índice
                            'estado': producto_result[5]  # Acceder por índice
                        })
                recomendaciones[recomendacion_id]['productos'].append(productos)

            return list(recomendaciones.values())
    except Exception as error:
        print(f"Error: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el historial de recomendaciones")