from schemas.imports import *
from pydantic import Field
import time
from security.hash import hash_password
class UserBase(BaseModel):
    # Add other fields here 
    email:EmailStr
    password:str | bytes
    pass

class UserRefresh(BaseModel):
    # Add other fields here 
    refresh_token:str
    pass


class UserCreate(UserBase):
    # Add other fields here 
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))
    @model_validator(mode='after')
    def obscure_password(self):
        self.password=hash_password(self.password)
        return self
class UserUpdate(BaseModel):
    # Add other fields here 
    last_updated: int = Field(default_factory=lambda: int(time.time()))

class UserOut(UserBase):
    # Add other fields here 
    id: Optional[str] =None
    date_created: Optional[int] = None
    last_updated: Optional[int] = None
    refresh_token: Optional[str] =None
    access_token:Optional[str]=None
    @model_validator(mode='before')
    def set_dynamic_values(cls,values):
        if isinstance(values,dict):
            values['id']= str(values.get('_id'))
            return values
      
            
    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }