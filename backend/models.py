from pydantic import BaseModel,EmailStr

class register(BaseModel):
    name : str
    email :EmailStr
    password : str

class signin(BaseModel):
    email :EmailStr
    password : str

class ApplyRequest(BaseModel):
    label: str
    image: str

class BgRequest(BaseModel):
    image: str
    color: str
