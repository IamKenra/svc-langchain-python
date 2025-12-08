from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from src.clients.llm_client import llm_client
from src.schemas.serverSchema import ServerStatusRightNow

ParserStatusRightNow = PydanticOutputParser(pydantic_object=ServerStatusRightNow)

StatusRightNowTemplate = PromptTemplate(
     template="""
    The current server average performance statistics right now are:
    - CPUSage: {cpu}%
    - RAM Usage: {ram}%
    - Disk Usage: {disk}%

    You are an expert in managing IT inventory in a large company. Based on the above statistical data,
    perform an in-depth analysis and describe the current server condition. Provide RECOMMENDATIONS BRIEFLY AND INSIGHTFULLY in good and correct Indonesian.
    Examples of Conditions that can be given are:
    - The current server condition is good, there are no issues to be concerned about.
    - The current server condition needs attention to high CPU usage.
    - The current server condition needs monitoring and attention to high CPU,RAM usage.
    Make sure every response you give is always **CONSISTENT IN EVERY SENTENCE AND WORD**.
    You only need to analyze this message alone without looking at previous messages as your response is one-time only.
    {format_instructions}
    """,
   
    input_variables=["cpu", "ram", "disk"],
    partial_variables={"format_instructions": ParserStatusRightNow.get_format_instructions()}
)

PerdictiveMaintenance = PromptTemplate(
    template="""
    The current server average performance statistics right now are:
    - CPUSage: {cpu}%
    - RAM Usage: {ram}%
    - Disk Usage: {disk}%

    You are an expert in managing IT inventory in a large company. Based on the above statistical data,
    perform an in-depth analysis and describe the current server condition. Provide RECOMMENDATIONS BRIEFLY AND INSIGHTFULLY in good and correct Indonesian.
    Examples of Conditions that can be given are:
    - The current server condition is good, there are no issues to be concerned about.
    - The current server condition needs attention to high CPU usage.
    - The current server condition needs monitoring and attention to high CPU,RAM usage.
    Make sure every response you give is always **CONSISTENT IN EVERY SENTENCE AND WORD**.
    You only need to analyze this message alone without looking at previous messages as your response is one-time only.
    {format_instructions}
    """,
    input_variables=["cpu", "ram", "disk"],
    partial_variables={"format_instructions": ParserStatusRightNow.get_format_instructions()}
)


StatusRightNow = StatusRightNowTemplate | llm_client | ParserStatusRightNow
