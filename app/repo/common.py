from pydantic import BaseModel

__all__ = ("Error",)


class Error(BaseModel):
    message: str
