# Standard library imports
import os
from types import SimpleNamespace

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
        "content" : "Responds under 100 words."
    }
)

def stream_chat(history):
    stream = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=history,
        tools=tools,
        stream=True
    )

    full_response = ""
    calls = {}
    label_printed = False

    # Stream the response from the model
    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 1. Content streaming
            if delta.content:
                if not label_printed:
                    print("\n🤖 Assistant: ", end="", flush=True)
                    label_printed = True
                print(delta.content, end="", flush=True)
                full_response += delta.content

            # 2. Tool call streaming
            for tc in (delta.tool_calls or []):
                obj = calls.setdefault(
                    tc.index,
                    SimpleNamespace(id=None, function=SimpleNamespace(name="", arguments="")),
                )
                if tc.id:
                    obj.id = tc.id
                if tc.function and tc.function.name:
                    obj.function.name += tc.function.name
                if tc.function and tc.function.arguments:
                    obj.function.arguments += tc.function.arguments

    except KeyboardInterrupt:
        print("\nStreaming interrupted by user.")
        calls = {}

    if label_printed:
        print()  # Move to the next line after streaming

    calls_list = []
    for key in sorted(calls):
        calls_list.append(calls[key])

    return full_response, calls_list


def build_tool_calls_payload(tool_calls):
    """
    Converts our collected tool calls into the dict format
    that the API expects inside an assistant message.
    """

    payload = []
    for tool_call in tool_calls:
        tool_call_dict = {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments
            }
        }
        payload.append(tool_call_dict)

    return payload


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

        full_response, tool_calls = stream_chat(messages)

        if not tool_calls:
            break

        log(f"Step {tool_call_count + 1}: model requested {len(tool_calls)} tool calls.")

        messages.append({
            "role": "assistant",
            "content": full_response,
            "tool_calls": build_tool_calls_payload(tool_calls)
        })

        for tool_call in tool_calls:
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
            "content": full_response
        }
    )