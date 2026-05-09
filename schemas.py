'''req/resp formats'''

from pydantic import BaseModel, HttpUrl

class URLRequest(BaseModel):
    url: HttpUrl
    custom_alias: str | None = None

class URLResponse(BaseModel):
    short_url: HttpUrl