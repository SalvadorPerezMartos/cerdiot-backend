from pydantic import BaseModel


class ShedBase(BaseModel):
    name: str


class ShedCreate(ShedBase):
    farm_id: int


class ShedOut(ShedBase):
    id: int
    farm_id: int

    class Config:
        from_attributes = True
