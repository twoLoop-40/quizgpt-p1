import json

from langchain_core.utils.function_calling import convert_to_openai_tool


def multiply(a: int, b: int) -> int:
    """Multiply two integers together

    Args:
        a: First integer
        b: Second integer
    """
    return a * b


print(json.dumps(convert_to_openai_tool(multiply), indent=2))

