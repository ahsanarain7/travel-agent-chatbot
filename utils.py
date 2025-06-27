from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
from agno.tools.serpapi import SerpApiTools

def getSearchTool(search_tool: str, api_key_search_tool: str) -> object:
    """
    Returns an instance of the specified search tool.
    
    Args:
        search_tool (str): The name of the search tool ('Tavily' or 'SerpApi').
        api_key_search_tool (str): The API key for the search tool.
    
    Returns:
        object: An instance of the specified search tool.
    
    Raises:
        ValueError: If the search tool is not recognized.
    """
    if search_tool == 'Tavily':
        return TavilyTools(api_key=api_key_search_tool)
    elif search_tool == 'SerpApi':
        return SerpApiTools(api_key=api_key_search_tool)
    else:
        raise ValueError(f"Unknown search tool: {search_tool}")

def getModel(llm_mode: str, api_key_llm: str) -> object:
    """
    Returns an instance of the specified language model.
    
    Args:
        llm_mode (str): The name of the language model ('OpenAI' or 'Groq').
        api_key_llm (str): The API key for the language model.
    
    Returns:
        object: An instance of the specified language model.
    
    Raises:
        ValueError: If the language model is not recognized.
    """
    if llm_mode == 'OpenAI':
        return OpenAIChat(id="gpt-4o", api_key=api_key_llm)
    elif llm_mode == 'Groq':
        return Groq(id="llama-3.3-70b-versatile", api_key=api_key_llm)
    else:
        raise ValueError(f"Unknown language model: {llm_mode}")