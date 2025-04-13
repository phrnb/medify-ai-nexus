
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    two_factor_required: bool = False

class TokenPayload(BaseModel):
    sub: str
    exp: int
    two_factor_verified: bool = False

class RefreshToken(BaseModel):
    refresh_token: str

class TwoFactorToken(BaseModel):
    code: str
