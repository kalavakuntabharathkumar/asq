from pydantic import BaseModel, Field, field_validator
from typing import Literal

class IngestTextRequest(BaseModel):
    source: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=20)

class GenerateRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=200)
    count: int = Field(default=5, ge=1, le=10)
    difficulty: Literal["easy", "medium", "hard"] = "medium"

class MCQ(BaseModel):
    question: str = Field(min_length=8)
    options: list[str] = Field(min_length=4, max_length=4)
    answer: str
    explanation: str = Field(min_length=3)
    source_excerpt: str = Field(min_length=3)

    @field_validator("options")
    @classmethod
    def unique_options(cls, value):
        if len({v.strip().casefold() for v in value}) != 4:
            raise ValueError("Options must be unique")
        return value

    @field_validator("answer")
    @classmethod
    def answer_is_option(cls, value, info):
        options = info.data.get("options", [])
        if options and value not in options:
            raise ValueError("Answer must exactly match one option")
        return value

class GenerateResponse(BaseModel):
    topic: str
    questions: list[MCQ]
    retrieved_chunks: int
    mode: str

class IngestResponse(BaseModel):
    source: str
    chunks_added: int
