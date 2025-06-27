from agno.agent import Agent, RunResponse
import json
from instructions import Instructions
from utils import getModel

MESSAGE_SUFFIX = "\n-If any of these parameters are missing, please create a conversational response for the user to provide them and include it in the 'message' key of the output JSON."

class TripConversationAgent(Agent):
    """
    An agent that converses with users to extract structured trip requirements.
    """
    
    def __init__(self, api_key: str, llm_mode: str):
        """
        Initialize the TripConversationAgent.

        Args:
            api_key (str): API key for the LLM.
            llm_mode (str): Mode to select the LLM model.
        """
        super().__init__(
            name="Conversational Trip Data Extractor",
            description="Converses with users to extract trip requirements in a structured format.",
            model=getModel(llm_mode, api_key),
            instructions=Instructions.CONVERSATION_INSTRUCTIONS,
            add_datetime_to_instructions=True
        )
        self.final_params = {
            "trip_type": None,
            "origin": None,
            "destination": None,
            "dates": None,
            "travelers": None,
            "accommodation": None,
            "budget": None,
            "requirements": None
        }
        self.final_param_keys = list(self.final_params.keys())
        self.suffix = ""

    def __process_tripdata(self, params_llm: dict) -> dict:
        """
        Process LLM-extracted parameters and identify missing ones.

        Args:
            params_llm (dict): Parameters extracted by the LLM.

        Returns:
            dict: Contains user message, query suffix, and missing status.
        """
        missing = []
        for key in self.final_param_keys:
            if not self.final_params[key]:  # Only update if not already set
                if key in params_llm and params_llm[key]:
                    self.final_params[key] = params_llm[key]
                else:
                    missing.append(key)

        if missing:
            missing_params = ", ".join(missing)
            return {
                "user_message": f"Please provide the following missing details: {missing_params}.",
                "query_suffix": f"\n-Identify only the following parameters: {missing_params} and return them in the output JSON.{MESSAGE_SUFFIX}",
                "missing": True
            }
        return {
            "user_message": "Thank you! Planning your trip...",
            "query_suffix": "",
            "missing": False
        }

    def reset(self):
        """
        Reset the agent's state for a new conversation.
        """
        self.final_params = {
            "trip_type": None,
            "origin": None,
            "destination": None,
            "dates": None,
            "travelers": None,
            "accommodation": None,
            "budget": None,
            "requirements": None
        }
        self.suffix = ""

    def process_query(self, query: str) -> dict:
        """
        Process user query to extract trip parameters.

        Args:
            query (str): User's input query.

        Returns:
            dict: Contains message, conversation status, and extracted data.
        """
        if not self.suffix:
            keys = ", ".join(self.final_param_keys)
            final_query = f"{query}\n-Identify only the following parameters: {keys} and return them in the output JSON.{MESSAGE_SUFFIX}"
        else:
            final_query = f"{query}\n{self.suffix}"

        try:
            response: RunResponse = self.run(final_query)
            # Extract JSON content from response
            content = response.content
            # Remove code block markers and model-specific tags
            for marker in ["```json", "```", "</think>", "<think>"]:
                content = content.replace(marker, "")
            content = content.strip()

            params = json.loads(content)

            # Validate that only allowed keys are present
            allowed_keys = set(self.final_param_keys) | {"message"}
            if not all(k in allowed_keys for k in params.keys()):
                raise ValueError("LLM returned unexpected keys in JSON.")

            result = self.__process_tripdata(params)
            self.suffix = result["query_suffix"]
            user_message = result["user_message"]
            have_further_conversation = result["missing"]

            # Use LLM-provided message if available and conversation continues
            if "message" in params and params["message"] and have_further_conversation:
                user_message = params["message"]

            return {
                "message": user_message,
                "have_further_conversation": have_further_conversation,
                "data": self.final_params
            }

        except json.JSONDecodeError:
            return {
                "message": "Sorry, I couldn't process your request. Please try again with clear details.",
                "have_further_conversation": True,
                "data": self.final_params
            }
        except ValueError as e:
            return {
                "message": f"Error: {str(e)}. Please provide your trip details again.",
                "have_further_conversation": True,
                "data": self.final_params
            }
        except Exception as e:
            return {
                "message": f"An unexpected error occurred: {str(e)}. Please try again.",
                "have_further_conversation": True,
                "data": self.final_params
            }