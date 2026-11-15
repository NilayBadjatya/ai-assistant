# Standard library imports
import os

# Third-party imports
from openai import OpenAI
from dotenv import load_dotenv

# Local application imports
from tools import tools, run_tool
from Utilities.utilities import log

load_dotenv()

client = OpenAI(
    base_url = os.getenv("BASE_URL"),
    api_key = os.getenv("API_KEY")
)

# Store the converstaion history in a list of messages
messages = []

MAX_STEPS = 10

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

        log(f"Step {tool_call_count + 1}: model requested {len(msg.tool_calls)} tool calls.")

        messages.append(msg)

        for tool_call in msg.tool_calls:
            result = run_tool(tool_call)
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