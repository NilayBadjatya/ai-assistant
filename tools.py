from datetime import datetime
from zoneinfo import ZoneInfo

def get_current_time(country: str) -> str:
    """Returns the current time for a given time zone."""
    current_time = datetime.now(ZoneInfo(country))
    return current_time.strftime("%Y-%m-%d %H:%M:%S")


tools = [
    {
        "type" : "function",
        "function" : {
            "name" : "get_current_time",
            "description" : "Returns the current time as a string in the format 'YYYY-MM-DD HH:MM:SS'.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "country" : {
                        "type" : "string",
                        "description" : (
                            "IANA timezone name for the location, such as "
                            "Asia/Kolkata or America/New_York."
                        )
                    }
                },
                "required" : ["country"],
                "additionalProperties" : False,
            }
        }
    }
]


function_map = {
    "get_current_time" : get_current_time
}  