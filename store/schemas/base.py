from pydantic import BaseModel


class BaseSchemaMixin(BaseModel):
    class Config:
        from_attributes = True
