from pydantic import BaseModel, Field

class AdminBase(BaseModel):
    username: str
    password: str

class AdminCreate(AdminBase):
    pass

class Admin(AdminBase):
    id: int

    class Config:
        orm_mode = True

class AdminUpdate(AdminBase):

    class Config:
        orm_mode = True

class AdminLogin(AdminBase):
    pass
