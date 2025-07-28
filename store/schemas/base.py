from datetime import datetime, timezone
from decimal import Decimal
from bson import Decimal128
from pydantic import UUID4, BaseModel, Field, model_validator


class BaseSchemaMixin(BaseModel):
    model_config = {
        "from_attributes": True,
        "json_encoders": {Decimal128: lambda v: str(Decimal(str(v)))},
    }


class OutSchema(BaseModel):
    id: UUID4 = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()

    @model_validator(mode="before")
    def set_schema(cls, data):
        for key, value in data.items():
            if isinstance(value, Decimal128):
                data[key] = Decimal(str(value))
            elif isinstance(value, datetime) and value.tzinfo is None:
                data[key] = value.replace(tzinfo=timezone.utc)
        return data
