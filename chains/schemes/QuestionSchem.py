from typing import Literal, Union
from pydantic import BaseModel, Field

class Question(BaseModel):
    question: str = Field(
        description="The generated question based on the given context."
    )
    question_type: Literal["T/F", "MCQ"] = Field(
        description="The type of question to be generated. Must be either 'T/F' (True/False) or 'MCQ' (Multiple Choice Question)."
    )
    options: Union[list[str], None] = Field(
        description="The list of answer choices for MCQ questions should be a newline-separated string such as 'A. Option1 B. Option2 nC. Option3 D. Option4'. Use 'None' for T/F questions."
    )
    answer: str = Field(
        description="The correct answer to the question. Must be 'True' or 'False' for T/F, or a single option identifier like 'A', 'B', etc. for MCQs."
    )
    explanation: str = Field(
        description="A concise explanation of why the selected answer is correct, based on the provided context."
    )

    def format(self) -> str:
        """
        Returns a structured string for display or logging.
        """
        return f"Question: {self.question}\nOptions: {self.options}\nAnswer: {self.answer}\nExplanation: {self.explanation}\n"

class Feedback(BaseModel):
    feedback: str = Field(
        description="feedback about the generated or refined question, such as accuracy, clarity, or educational value."
    )

    def format(self) -> str:
        """
        Formats the feedback message.
        """
        return f"Feedback: {self.feedback}\n"

class GradeQuestion(BaseModel):
    """Represents the grading information for a question."""

    score: str = Field(
        description="The score assigned to the question based on its relevance and quality. Must be 'Yes' or 'No'."
    )
