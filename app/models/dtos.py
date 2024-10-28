from typing import Generic, List, TypeVar
from pydantic import BaseModel

from app.models.models import Producto


class ErrorResponseDTO(BaseModel):
    status_code: int
    detail: str

T = TypeVar('T')
class ModelResponseDTO(BaseModel, Generic[T] ):
    status_code: int
    detail: str
    data: list[T] | T 

class LoginDto(BaseModel):
    username: str
    password: str

class RecommendationRequestDTO(BaseModel):
    peso: float
    altura: float
    edad: int
    genero: int
    nivel_actividad: int

class RecommendationResponseDTO(BaseModel):
    combinacion_recomendada: List[float]
    productos_recomendados: List[Producto]
    distancia: float