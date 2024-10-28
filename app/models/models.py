from pydantic import BaseModel, EmailStr
from typing import Optional

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
    estado: int


