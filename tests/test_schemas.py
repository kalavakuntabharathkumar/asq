import pytest
from pydantic import ValidationError
from app.schemas import MCQ, GenerateRequest

def test_mcq_valid():
    q = MCQ(question="What is described in the passage?", options=["A", "B", "C", "D"],
            answer="A", explanation="The source supports A.", source_excerpt="A appears in the source.")
    assert q.answer == "A"

def test_answer_must_be_an_option():
    with pytest.raises(ValidationError):
        MCQ(question="What is described in the passage?", options=["A", "B", "C", "D"],
            answer="E", explanation="A short explanation.", source_excerpt="A source excerpt.")

def test_count_is_bounded():
    with pytest.raises(ValidationError):
        GenerateRequest(topic="biology", count=100)
