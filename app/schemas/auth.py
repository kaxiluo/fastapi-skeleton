from pydantic import BaseModel


class Token(BaseModel):
    token_type: str
    expires_in: int
    access_token: str
