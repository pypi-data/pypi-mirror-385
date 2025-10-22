from pydantic import BaseModel, Field


class ResultText(BaseModel):
    text: str = Field(...)


class ResultModel(BaseModel):
    result: ResultText = Field(...)
