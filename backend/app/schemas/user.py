"""
User schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="이메일 주소")
    username: str = Field(..., min_length=3, max_length=100, description="사용자명")
    password: str = Field(..., min_length=8, max_length=100, description="비밀번호")
    full_name: Optional[str] = Field(None, max_length=255, description="이름")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v:
            raise ValueError('이메일을 입력해주세요')
        return v.lower()
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('사용자명은 3자 이상이어야 합니다')
        if len(v) > 100:
            raise ValueError('사용자명은 100자 이하여야 합니다')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('사용자명은 영문, 숫자, 밑줄(_)만 사용할 수 있습니다')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('비밀번호는 8자 이상이어야 합니다')
        if len(v) > 100:
            raise ValueError('비밀번호는 100자 이하여야 합니다')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str

