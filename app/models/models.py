from pydantic import BaseModel, EmailStr
from typing import List, Optional

# Modelos
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserInDB(BaseModel):
    id: Optional[int]
    nombres: str
    apellidos: str
    correo: EmailStr
    contrasenia: str

class UserCreate(BaseModel):
    nombres: str
    apellidos: str
    correo: EmailStr
    contrasenia: str

class Producto(BaseModel):
    id: Optional[int]
    nombre: str
    proteinas: float
    grasas: float
    carbohidratos: float
    estado: Optional[int] = None  # Hacer el campo estado opcional

class HistorialRecomendacionResponse(BaseModel):
    id: int
    usuario_id: int
    peso: float
    talla: float
    edad: int
    genero: int
    act_fisica: int
    imc: float
    f_recomendacion: str
    productos: List[List[Producto]]  # Cambiar a lista de listas de enteros

