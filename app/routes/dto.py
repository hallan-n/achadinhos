from pydantic import BaseModel, Field


class PostLogin(BaseModel):
    user: str = Field(..., min_length=3)
    password: str = Field(..., min_length=3)
    role: str = Field(..., min_length=3)
    url_base_site: str = ''
    url_base_affiliate: str = ''


class GetLogin(PostLogin):
    id: int
