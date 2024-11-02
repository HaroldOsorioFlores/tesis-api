from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.models.dtos import ModelResponseDTO
from app.models.models import TokenData, UserInDB
from app.db.db_connection import get_db



SECRET_KEY = "tu_clave_secreta_muy_segura_y_larga" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

async def get_user_by_email(email: str, connection) -> Optional[UserInDB]:
    async with connection.cursor() as cursor:
        query = """
            SELECT id, nombres, apellidos, correo, contrasenia FROM usuarios WHERE correo = %s
        """
        await cursor.execute(query, (email,))
        result = await cursor.fetchone()

        if result:
            return UserInDB(
                id=result[0],
                nombres=result[1],
                apellidos=result[2],
                correo=result[3],
                contrasenia=result[4],
            )
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    connection = Depends(get_db)
):
    print(f"Token recibido: {token}") 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(email=token_data.email, connection=connection)
    if user is None:
        raise credentials_exception
    
    user_model = ModelResponseDTO[UserInDB](
        data=user,
        detail="Usuario iniciado sesión correctamente",
        status_code=status.HTTP_200_OK
    )
    return user_model

async def get_current_active_user(
    current_user: Annotated[ModelResponseDTO, Depends(get_current_user)],
):
    if current_user.data.contrasenia is None:  
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
