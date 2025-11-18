from pydantic import BaseModel, EmailStr, Field, field_validator

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(
        ..., 
        min_length=6,
        max_length=50,
        description="Password must be 6-50 characters"
    )
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Password cannot be empty')
        
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password too long (max 72 bytes)')
        
        return v.strip()

class User(UserBase):
    id: int
    username: str
    full_name: str | None = None

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    """OAuth2 token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """JWT token payload"""
    email: str | None = None