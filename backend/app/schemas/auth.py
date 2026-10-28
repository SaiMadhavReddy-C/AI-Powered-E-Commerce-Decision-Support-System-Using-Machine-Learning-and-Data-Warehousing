from pydantic import BaseModel


class OtpRequest(BaseModel):
    email: str


class OtpVerifyRequest(BaseModel):
    email: str
    code: str
