from app.database.setup import Base
from sqlalchemy.orm import Mapped , mapped_column 
from sqlalchemy import String , DateTime , func 
from enum import Enum
from sqlalchemy import Enum as SQLENUM


class Roles(Enum):
    admin = "admin"
    agent = "agent"
    tenant = "tenant"

class User(Base):
    __tablename__ = 'users'

    id : Mapped[int] = mapped_column(primary_key=True)
    username : Mapped[str] = mapped_column(String(255),nullable=False)
    email : Mapped[str] = mapped_column(unique=True,nullable=False)
    password : Mapped[str] = mapped_column(nullable=False)
    roles : Mapped[Roles] = mapped_column(SQLENUM(Roles , name="roles_enum"), server_default=Roles.tenant.value)
    created_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class Organization(Base):
    __tablename__ = "Organization"

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(255) , nullable=True)
    created_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

