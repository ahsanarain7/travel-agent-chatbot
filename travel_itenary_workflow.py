from agno.agent import Agent, RunResponse
from agno.utils.log import logger
from agno.workflow import Workflow
from instructions import Instructions
from utils import getModel, getSearchTool
import json

class ItenaryGeneratorWorkflow(Workflow):
    description: str = "Comprehensive Travel Itinerary Workflow"
    
    def __init__(self, api_key_llm: str, api_key_search_tool: str, search_tool: str, llm_mode: str):
        self.travel_query_generator: Agent = Agent(
            name="Travel Query Enhancer",
            description="Generates structured trip-specific queries",
            instructions=Instructions.QUERY_ENHANCER_INSTRUCTIONS,
            model=getModel(llm_mode, api_key_llm),
            debug_mode=False,
            add_datetime_to_instructions=True
        )
        
        self.researcher = Agent(
            name="Travel Data Gatherer",
            description="Collects real-time travel data and local information",
            instructions=Instructions.RESEARCH_INSTRUCTIONS,
            tools=[getSearchTool(search_tool=search_tool, api_key_search_tool=api_key_search_tool)],
            model=getModel(llm_mode, api_key_llm),
            debug_mode=False,
            add_datetime_to_instructions=True
        )
        
        self.travel_agent = Agent(
            name="Itinerary Compiler",
            description="Generates visually appealing markdown itinerary",
            instructions=Instructions.ITINERARY_INSTRUCTIONS,
            model=getModel(llm_mode, api_key_llm),
            markdown=True,
            debug_mode=False,
            add_datetime_to_instructions=True
        )
    
    def __generate_trip_query(self, queryJSON):
        trip_type = queryJSON.get('trip_type', 'Holiday')
        origin = queryJSON.get('origin', 'unspecified')
        destination = queryJSON.get('destination', 'unspecified')
        start_date = queryJSON.get('dates', {}).get('start_date', 'unspecified')
        end_date = queryJSON.get('dates', {}).get('end_date', 'unspecified')

        travelers = queryJSON.get('travelers')
        if isinstance(travelers, dict):
            adults = travelers.get('adults', 0)
            children = travelers.get('children', 0)
        else:
            adults = 0
            children = 0

        budget = queryJSON.get('budget', 'unspecified')
        requirements = queryJSON.get('requirements', 'none')
        
        travelers_str = f"{adults} adults"
        if children > 0:
            travelers_str += f" and {children} children"
        
        query = f"""I want to plan a {trip_type} trip from {origin} to {destination} 
                    from {start_date} to {end_date} 
                    for {travelers_str}. 
                    Budget: {budget}.
                    Special requirements: {requirements}.
                    Please include multiple options for flights, accommodation, and transportation."""
        return query
    
    def run(self, payload: str) -> RunResponse:
        if isinstance(payload, str):
            try:
                queryJSON = json.loads(payload)
            except json.JSONDecodeError:
                return RunResponse(content="Invalid JSON payload", status="error")
        else:
            queryJSON = payload
        
        raw_query = self.__generate_trip_query(queryJSON)
        
        try:
            enhanced_query = self.travel_query_generator.run(raw_query)
        except Exception as e:
            return RunResponse(content=f"Error in query enhancement: {str(e)}", status="error")
        
        try:
            data = self.researcher.run(enhanced_query.content)
        except Exception as e:
            return RunResponse(content=f"Error in data gathering: {str(e)}", status="error")
        
        try:
            itinerary = self.travel_agent.run(data.content)
        except Exception as e:
            return RunResponse(content=f"Error in itinerary generation: {str(e)}", status="error")
        
        return itinerary
