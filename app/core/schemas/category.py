from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CategoryCreateSchema(BaseModel):
    name: str =  Field(max_length=30)


class CategoryResponseSchema(BaseModel):
    id: int = Field(gt=0)
    name: str

    model_config = ConfigDict(from_attributes=True)


class CategoryPartialUpdateSchema(BaseModel):
    name: Optional[str] = Field(max_length=30)
