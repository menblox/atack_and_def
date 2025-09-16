from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True)
    age: Mapped[int] = Column(Integer)
    town: Mapped[str] = Column(String, index=True)
    hash_password: Mapped[str] = Column(String)

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String, index=True)
    body: Mapped[str] = Column(String)
    author_id: Mapped[int] = Column(Integer, ForeignKey("users.id"))

    author: Mapped["User"] = relationship("User")