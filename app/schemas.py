from pydantic import BaseModel, EmailStr, conint
from typing import Annotated
from datetime import datetime


class PostBase(BaseModel):
    title: str 
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    id: int 
    email: EmailStr
    created_at: datetime 
    class config:
        from_attributes = True
        


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        from_attributes = True

class PostOut(BaseModel):
    Post: Post
    votes: int 

    class Config:
        from_attributes = True
       

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str 
    token_type: str 

class TokenData(BaseModel):
    user_id: int


class Vote(BaseModel):
    post_id: int 
    dir: Annotated[int, conint(le=1)]