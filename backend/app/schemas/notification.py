from pydantic import BaseModel


class TestEmailRequest(BaseModel):
    recipient: str
