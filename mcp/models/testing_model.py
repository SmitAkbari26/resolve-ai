from pydantic import BaseModel


class SumNumbersRequest(BaseModel):
    a: float
    b: float


class SumResponse(BaseModel):
    operation: str
    a: float
    b: float
    result: float
