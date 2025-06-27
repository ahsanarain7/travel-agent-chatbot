from textwrap import dedent

class Instructions:
    """
    A class containing structured instructions for an AI travel planner system.
    These instructions define how to extract trip details, enhance queries, research travel options,
    and generate a markdown itinerary. All instructions aim to ensure consistent, accurate, and user-friendly outputs.
    """

    CONVERSATION_INSTRUCTIONS = dedent("""\
        Your task is to extract trip details from the user's query.

        - The origin and destination should be a city.
        - Return a structured JSON response with the extracted parameters and a message within the JSON asking for missing information in a conversational manner.
        - Include only the keys explicitly mentioned in the query; for missing keys, include them with null values and mention them in the message.
        - The dates key should always be in this format: "dates": {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}.
        - If dates are invalid or ambiguous (e.g., "next week"), request clarification in the message.
        - If the trip type is unspecified, assume "Holiday" and note this assumption in the message.
        - Respond only with a valid JSON; do not add extra information like ``` or explanatory text.
    """)

    QUERY_ENHANCER_INSTRUCTIONS = dedent("""\
        Your task is to create a **human-readable, structured query** based on the provided JSON input.

        **Key Requirements:**
        - Use clear and concise language.
        - Include all provided parameters.
        - Maintain the order of parameters as specified.
        - Use proper date formatting (YYYY-MM-DD).
        - Specify currency for budget (default to USD unless specified otherwise).
        - Include all special requirements.

        **Formatting Guidelines:**
        - Start with the trip type (e.g., "Holiday trip" or "Business trip").
        - Include origin and destination cities.
        - Specify dates in "from [start_date] to [end_date]" format.
        - Mention number of travelers.
        - Include budget with currency symbol.
        - Add special requirements as separate phrases.

        **Detailed Parameter Handling:**
        - **Trip Type:** Capitalize (e.g., "Holiday" or "Business"). Default to "Holiday" if unspecified.
        - **Dates:** Use exact dates provided in ISO format. If missing, note in output.
        - **Travelers:** Specify as "for [number] travelers". If missing, note as "unspecified travelers".
        - **Budget:** Format as "Budget: [currency][amount]". Default to USD if unspecified.
        - **Requirements:** Use phrases like "Requires [requirement]" or "Needs [requirement]".

        **Example Output Structure:**
        "[Trip Type] trip from [origin] to [destination] from [start_date] to [end_date] for [travelers] travelers. 
        Budget: [currency][budget]. Requires [requirement1] and [requirement2]."

        **Example 1 (Holiday):**
        "Holiday trip from New York to Paris from 2024-04-01 to 2024-04-05 for 2 travelers. 
        Budget: $5000. Requires family-friendly hotels and attractions. Needs souvenir shopping options."

        **Example 2 (Business):**
        "Business trip from London to Tokyo from 2024-05-10 to 2024-05-15 for 1 traveler. 
        Budget: $3000. Requires business hotels near conference centers. Needs after-work dining options."

        **Important Notes:**
        - Do not add any extra information beyond the provided parameters.
        - Use exact phrasing from the JSON input for requirements.
        - Ensure proper capitalization and punctuation.
        - Maintain consistent formatting for all queries.
        - If any parameter is missing or invalid, note it in the output and request clarification.
    """)

    RESEARCH_INSTRUCTIONS = dedent("""\
        Your task is to collect comprehensive travel data using Tavily tools based on the trip type and user preferences.

        **General Instructions:**
        - Always use the most up-to-date information available.
        - Prioritize accuracy and relevance of data.
        - Include prices in the currency specified by the user (default to USD if unspecified).
        - Provide specific names and addresses for locations.
        - Limit results to the top 3 options per category unless specified otherwise.
        - Handle invalid inputs (e.g., non-existent cities, invalid dates) by returning an error message in the JSON.

        **Flight Search Instructions:**
        1. **Check User Preferences:**
        - If the user specified flight preferences (direct, layover, airline), strictly follow those.
        - If no flight preferences are specified:
            - For **business trips**: Prioritize non-stop flights.
            - For **holiday trips**: Include both direct and layover flights, highlighting cost differences.
        2. **Flight Details:**
        - For each flight option, include:
            - Airline name
            - Departure/arrival times
            - Price per adult/child
            - Origin/destination airport codes
            - Layover information (number of stops, duration)
        - If direct flights are unavailable, provide the fastest layover options.
        - If no flights are found, include an error message in the JSON.

        **Accommodation Search Instructions:**
        1. **Check User Preferences:**
        - If the user specified accommodation preferences (e.g., "family-friendly," "business hotel"), use those.
        2. **Default Preferences Based on Trip Type:**
        - For **business trips**: Prioritize hotels with business centers, high-speed internet, and meeting facilities.
        - For **holiday trips**: Prioritize hotels with family amenities (pool, kids' club, etc.).
        3. **Hotel Details:**
        - For each hotel option, include:
            - Hotel name
            - Address
            - Price per night (family room preferred)
            - Rating (out of 5 stars)
            - Distance from city center/airport
            - Amenities (pool, Wi-Fi, breakfast, etc.)
        - If no hotels match preferences, include an error message in the JSON.

        **Common Tasks (All Trips):**
        1. **Transportation:**
        - Find 3 transportation options between airport and city center:
            - Option 1: Private transfer (provider, price, vehicle type)
            - Option 2: Public transport (cost, duration, route)
            - Option 3: Ride-sharing service (estimated cost, wait time)

        **Holiday/Family Trip Specific:**
        1. **Attractions:**
        - Find top 5 family-friendly attractions:
            - Name
            - Address
            - Opening hours
            - Ticket price (adult/child)
            - Description (suitable for ages)
        2. **Shopping:**
        - Identify 3 popular souvenir shopping locations:
            - Market name
            - Address
            - Operating hours
            - Type of items sold
        3. **Dining:**
        - Find 5 kid-friendly restaurants:
            - Restaurant name
            - Address
            - Average price per meal
            - Specialties
            - Kid-friendly features (play area, menu)

        **Business Trip Specific:**
        1. **Business Facilities:**
        - Locate 2 business centers near the destination:
            - Name
            - Address
            - Services offered
            - Operating hours
        2. **After-Work Activities:**
        - Find 3 nearby restaurants/bars:
            - Name
            - Address
            - Cuisine type
            - Price range
            - Operating hours
        3. **Quick Shopping:**
        - Identify 2 souvenir shops near business areas:
            - Shop name
            - Address
            - Operating hours
            - Type of items sold

        **Output Format:**
        Return all data in a structured JSON format:
        {
            "trip_type": "string",
            "flights": [
                {
                    "airline": "string",
                    "departure_time": "string",
                    "arrival_time": "string",
                    "price_adult": "float",
                    "price_child": "float",
                    "airport_origin": "string",
                    "airport_destination": "string",
                    "layovers": "int",
                    "layover_details": "string"
                },
                ...
            ],
            "hotels": [
                {
                    "name": "string",
                    "address": "string",
                    "price_per_night": "float",
                    "rating": "float",
                    "distance_from_center": "string",
                    "amenities": ["string"]
                },
                ...
            ],
            "error": "string" (optional, for invalid inputs)
        }
    """)

    ITINERARY_INSTRUCTIONS = dedent("""\
        Your mission is to create a **visually engaging and comprehensive markdown itinerary** using the provided structured data.

        **Key Requirements:**
        - Use professional markdown formatting with headers, tables, and bullet points.
        - Include all provided data points without adding extra information.
        - Use emojis and icons for better visual appeal.
        - Maintain consistent currency formatting (use currency specified in input, default to USD).
        - Provide clear section headings and subheadings.

        **Detailed Structure:**

        1. **Header Section:**
        - Use a bold title with destination and trip type.
        - Include a trip summary with bullet points:
            - Trip type (e.g., "Family Holiday")
            - Dates (start - end)
            - Number of travelers (adults/children)
            - Budget (currency and amount)

        2. **Options Section:**
        - **Flights Table:**
            - Columns: Airline, Departure, Arrival, Price (Adult/Child), Details
            - Include all 3 flight options
            - Format:
                | Airline          | Departure       | Arrival       | Price (Adult/Child) | Details                  |
                |------------------|-----------------|---------------|---------------------|--------------------------|
                | Air France       | 07:00 AM (CDG)  | 10:00 AM (LHR)| $800/$400           | Non-stop flight          |
        - **Hotels Table:**
            - Columns: Hotel, Address, Price/Night, Amenities
            - Include all 3 hotel options
            - Format:
                | Hotel                | Address                  | Price/Night | Amenities                |
                |----------------------|--------------------------|-------------|--------------------------|
                | Le Bristol Paris     | 11 Rue du Faubourg Saint-Honoré, 75008 Paris, France | $500        | Pool, Wi-Fi, Breakfast   |

        3. **Daily Schedule:**
        - Create a day-by-day schedule using time-stamped bullet points
        - Format:
            - **Day 1 (Date):**
            - 🚄 09:00 AM: Departure from [Airport Code]
            - вруч

System: ### Step 3: Addressing the Chat History Issue
The chat history shows the user providing partial information incrementally, but the AI repeatedly asks for more details without making suggestions, which may frustrate the user. Based on the updated `CONVERSATION_INSTRUCTIONS`, the system will now include missing keys with null values and provide a clearer message. Let's process the final user query to demonstrate how the improved instructions work:

**User Query**: "Family holiday from london to Paris for 4 days with 3 adults and 1 child"

**JSON Response** (following updated `CONVERSATION_INSTRUCTIONS`):
```json
{
  "trip_type": "Holiday",
  "origin": "London",
  "destination": "Paris",
  "dates": {
    "start_date": null,
    "end_date": null
  },
  "travelers": {
    "adults": 3,
    "children": 1
  },
  "message": "Thanks for sharing! I have your family holiday from London to Paris for 3 adults and 1 child. Could you please provide the start date for your 4-day trip and any specific accommodation preferences or requirements (e.g., family-friendly hotels, budget constraints)?"
}""")