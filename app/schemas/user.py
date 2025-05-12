from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    address: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    name: str
    address: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    address: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
