import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from tools import tools, function_map

load_dotenv()

client = OpenAI(
    base_url = os.getenv("BASE_URL"),
    api_key = os.getenv("API_KEY")
)

# Store the converstaion history in a list of messages
messages = []

MAX_STEPS = 1

messages.append(
    {
        "role" : "system",
        "content" : "Responds under 20 words."
    }
)

while True:
    user_input = input("\nNilay: ")

    if(user_input.lower() == "bye"):
        print("Exiting the chat...")
        break

    messages.append(
        {
            "role": "user", 
            "content": user_input
        }
    )

    tool_call_count = 0
    # Chained Tool Calling(Agent Loop)
    while tool_call_count <= MAX_STEPS:

        response = client.chat.completions.create(
            model = os.getenv("MODEL"),
            messages = messages,
            tools = tools,
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            break

        messages.append(msg)

        for tool_call in msg.tool_calls:
            function_name = tool_call.function.name
            function_args =  {}

            try:
                function_args = json.loads(tool_call.function.arguments or "{}")
                function = function_map.get(function_name)
                result = function(**function_args) # Convert the arguments to a dictionary and pass them as keyword arguments ex: get_current_time(country="Asia/Kolkata") previously the function_args was like a string, now it is a dictionary.
            except Exception as e:
                result = f"Error calling function '{function_name}': {str(e)}"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                }
            )

        tool_call_count += 1  

    else:
        fallback = "Maximum tool call limit reached. Please try again with a different query."
        messages.append({
            "role": "assistant",
            "content": fallback
        })
        print(f"\nAssistant: {fallback}")
        continue

    messages.append(
        {
            "role": "assistant",
            "content": msg.content
        }
    )

    print(f"\nAssistant: {msg.content}")