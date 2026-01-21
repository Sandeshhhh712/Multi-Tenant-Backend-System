from fastapi import FastAPI , HTTPException , status
from contextlib import asynccontextmanager
from app.database.setup import Base , engine , SessionDependency 
from app.database.models import User
from app.database.schemas import UserCreate , UserRead
from app.authentication.auth import hash_password 
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select


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