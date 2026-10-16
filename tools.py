from datetime import datetime
import requests
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def get_city_weather(city):
    url=f"https://wttr.in/{city}?format=3"
    response = requests.get(url,timeout=10)
    return response.text
TOOLS=[
    {
        "type":"function",
        "function":{
            "name":"get_current_time",
            "description":"Returns current date and time as formatted string",
            "parameters":{}
        }
    },
    {
            "type":"function",
            "function":{
                "name":"get_city_weather",
                "description":"Returns current Weather for given city.",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "city":{
                            "type":"string",
                            "description":"the name of the city to get the weather."
                        }
                    }
                }
            }
        }
]

FUNCTION_NAME_TO_FUNCTION_MAP={
    "get_current_time":get_current_time,
    "get_city_weather":get_city_weather
}