from sqlalchemy.orm import DeclarativeBase , sessionmaker , Session
from sqlalchemy import create_engine 
from collections.abc import Generator
from fastapi import Depends
from typing import Annotated

class Base(DeclarativeBase):
    pass

database_url = 'sqlite:///database.db'

connect_args = {'check_same_thread':False}
engine = create_engine(database_url, connect_args=connect_args , echo=True)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

def get_session() -> Generator[Session , None , None]:
    session = SessionLocal()
    try:
        yield session # doing this returns a generator object not a Session object , thats why we specify return type as Generator
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

SessionDependency = Annotated[Session , Depends(get_session)]
