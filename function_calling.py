from typing import List
from typing import Optional, TypeVar, Generic
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv

T = TypeVar("T")
load_dotenv()


class Answer(BaseModel):
    """answer"""

    answer: str = Field(..., description="Answer")
    correct: bool = Field(..., description="Whether the answer is correct or not")


class Question(BaseModel):
    """question"""

    question: str = Field(..., description="Question")
    answers: List[Answer] = Field(..., description="Answers to the question")


class Questions(BaseModel):
    """questions collection"""

    questions: List[Question] = Field(..., description="List of questions")


class CreateQuiz(BaseModel):
    """function that takes a list of questions and answers and returns a quiz"""

    questions: Questions = Field(..., description="Questions for the quiz")


