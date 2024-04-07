import json
from typing import Type, Any

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool


class MultiplySchema(BaseModel):
    """Multiply tool schema."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


class Multiply(BaseTool):
    args_schema : Type[BaseModel] = MultiplySchema
    name: str = "multiply"
    description = "Multiply two integers together"

    def _run(self, a: int, b: int, **kwargs: Any) -> Any:
        return a * b


print(json.dumps(convert_to_openai_tool(Multiply()), indent=2))
