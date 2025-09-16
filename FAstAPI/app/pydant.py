from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    age: int
    town: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserForPost(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    body: str


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    author: UserForPost

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class Name_JWT(BaseModel):
    email: EmailStr

    class Config:
        from_attributes = True