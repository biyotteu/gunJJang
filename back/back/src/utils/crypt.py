from passlib.context import CryptContext
from typing import Any, Union
from datetime import datetime, timedelta
import jwt
from config import get_settings
from utils.logger import logger
import hashlib

def hash_fixed_seed(input_string):
    # SHA-256 해싱 객체 생성
    sha256 = hashlib.sha256()
    
    # 입력 문자열을 인코딩하여 해싱 객체에 업데이트
    sha256.update(input_string.encode('utf-8'))
    
    # 해싱된 결과를 16진수 문자열로 반환
    return sha256.hexdigest()

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fix_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload if payload else None
    except jwt.PyJWTError:
        return None