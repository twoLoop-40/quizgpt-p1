from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser, PydanticToolsParser
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class Multiply(BaseModel):
    """Multiply two integers together."""
    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
llm_with_tools = llm.bind_tools([Multiply])

tool_chain = llm_with_tools | PydanticToolsParser(tools=[Multiply])

res = tool_chain.invoke("What's 3*12")
print(res)