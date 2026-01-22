from pwdlib import PasswordHash
from app.database.setup import SessionDependency
from sqlalchemy import select
from app.database.models import User
from fastapi import HTTPException ,status , Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt 
from datetime import timedelta , timezone , datetime
from typing import Mapping , Any , Annotated 
from app.database.schemas import Tokendata
from jwt.exceptions import InvalidTokenError

SECRET_KEY = "0037d30fa1dc411dcc518fa0b97af5846273eb0485c741cff3d2881700bf3af2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")
password_hash = PasswordHash.recommended()

def verify_password(plain_password:str,hashed_password:str):
    return password_hash.verify(plain_password , hashed_password)

def hash_password(password:str):
    return password_hash.hash(password)

def get_user(session : SessionDependency , username : str) -> User | None:
    stmt =  select(User).where(User.username == username)
    return session.scalar(stmt)

def authenticate_user(session: SessionDependency , username : str , password : str) -> User | None:
    user = get_user(session, username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_password(password , user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password don't match"
        )
    return user
    
def create_access_token(data : Mapping[str,Any] , expires_delta : timedelta | None = None) -> str:
    if "sub" not in data:
        raise ValueError("JWT payload must include 'sub'")
    
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=15)
    )

    payload = dict(data)
    payload["exp"] = int(expire.timestamp())

    return jwt.encode(payload , SECRET_KEY , algorithm=ALGORITHM)

def get_current_user(token: Annotated[str , Depends(oauth2scheme)], session : SessionDependency):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not Validate Credentials",
        headers={'WWW-Authenticate':'Bearer'}
    )
    try:
        payload = jwt.decode(token , SECRET_KEY , algorithms=ALGORITHM)
        username = payload.get('sub')
        if username is None:
            raise credential_exception
        tokendata = Tokendata(username=username)
    except InvalidTokenError:
        raise credential_exception
    user = get_user(session , username=tokendata.username)
    if username is None:
        raise credential_exception
    return user
