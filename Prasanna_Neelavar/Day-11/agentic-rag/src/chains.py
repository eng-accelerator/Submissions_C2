from langchain_classic.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict, Any

# --- Pydantic Models for Structured Output ---

class TabularData(BaseModel):
    """Represents structured data in a tabular format."""
    columns: List[str] = Field(description="The column headers for the table.")
    data: List[List[Any]] = Field(description="The rows of the table, where each row is a list of values.")

class ChartData(BaseModel):
    """Represents data suitable for plotting a chart."""
    chart_type: str = Field(description="The type of chart to generate (e.g., 'bar', 'line', 'pie').")
    data: Dict[str, Any] = Field(description="The data for the chart, often in a format like {labels: [], values: []}.")

# --- Chain Implementations ---

def create_summarization_chain(llm: ChatOpenAI):
    """Creates a summarization chain."""
    return load_summarize_chain(llm, chain_type="map_reduce")

def create_tabular_chain(llm: ChatOpenAI):
    """Creates a chain that extracts tabular data based on a query."""
    parser = JsonOutputParser(pydantic_object=TabularData)
    prompt = ChatPromptTemplate.from_template(
        """Based on the following documents, extract the information needed to answer the user's query.\n"
        "User Query: {query}\n"
        "Documents: {context}\n"
        "{format_instructions}\n"""
    ).partial(format_instructions=parser.get_format_instructions())
    chain = prompt | llm | parser
    return chain

def create_chart_chain(llm: ChatOpenAI):
    """Creates a chain that generates chart data based on a query."""
    parser = JsonOutputParser(pydantic_object=ChartData)
    prompt = ChatPromptTemplate.from_template(
        """Based on the following documents, generate the data needed to create a chart for the user's query.\n"
        "User Query: {query}\n"
        "Documents: {context}\n"
        "{format_instructions}\n"""
    ).partial(format_instructions=parser.get_format_instructions())
    chain = prompt | llm | parser
    return chain
