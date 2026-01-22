from fastapi import FastAPI , HTTPException , status , Depends
from contextlib import asynccontextmanager
from app.database.setup import Base , engine , SessionDependency 
from app.database.models import User , Organization
from app.database.schemas import UserCreate , UserRead , Token , OrganizationCreate
from app.authentication.auth import require_admin , hash_password , authenticate_user , ACCESS_TOKEN_EXPIRE_MINUTES , create_access_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta


@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    
app = FastAPI(lifespan=lifespan)

@app.post("/user")
def create_user(session:SessionDependency, user : UserCreate ) -> UserRead:
    
    stmt = select(User).where(User.username == user.username)
    existing_user = session.scalar(stmt)


    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    hashed_password = hash_password(user.password)
    
    user_in = User(
        username = user.username,
        email = user.email,
        password = hashed_password

    )
    try:
        session.add(user_in)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists"
        )
    session.refresh(user_in)
    return UserRead.model_validate(user_in)

@app.post("/token")
def token(formdata : Annotated[OAuth2PasswordRequestForm , Depends()], session : SessionDependency) -> Token:
    user = authenticate_user(session ,formdata.username , formdata.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Username or Password",
            headers={'WWW-Authenticate':'Bearer'}
        )
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub':user.username}, expires_delta=access_token_expire)
    return Token(access_token=access_token , token_type='bearer')

@app.post("/organization")
def create_organization(organization : OrganizationCreate, session : SessionDependency , current_user : User = Depends(require_admin)):
    
    new_organization = Organization(
        name = organization.name
    )

    session.add(new_organization)
    session.commit()
    session.refresh(new_organization)
    return new_organization


