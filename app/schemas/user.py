from datetime import date, datetime
from pydantic import BaseModel
from typing import List, Literal

Gender = Literal["male", "female", "non_binary", "prefer_not_to_say", "other"]


class UserAddressBase(BaseModel):
    label: str = "Home"
    recipient_name: str | None = None
    phone_country_code: str | None = None
    phone_number: str | None = None
    line1: str
    line2: str | None = None
    city: str
    state: str | None = None
    postal_code: str | None = None
    country: str
    is_default: bool = False


class UserAddressCreate(UserAddressBase):
    pass


class UserAddressUpdate(BaseModel):
    label: str | None = None
    recipient_name: str | None = None
    phone_country_code: str | None = None
    phone_number: str | None = None
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    is_default: bool | None = None


class UserAddressResponse(UserAddressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class UserProfileBase(BaseModel):
    name: str
    phone_country_code: str | None = None
    phone_number: str | None = None
    birthday: date | None = None
    gender: Gender | None = None


class UserCreate(UserProfileBase):
    email: str
    password: str
    address: str | None = None
    primary_address: UserAddressCreate | None = None
    role: Literal["user", "admin"] = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(UserProfileBase):
    address: str | None = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    address: str | None = None
    phone_country_code: str | None = None
    phone_number: str | None = None
    birthday: date | None = None
    gender: Gender | None = None
    role: Literal["user", "admin"]
    addresses: List[UserAddressResponse] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


class PaginatedUsers(BaseModel):
    users: List[UserResponse]
    total: int
