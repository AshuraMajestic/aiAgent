import os 
from dotenv import load_dotenv

load_dotenv()
START_SEQUENCE="\033[91m"
END_SEQUENCE="\033[0m"

def log(text):
    if os.getenv("DEBUG", "").lower() == "true":
        print(f"  {START_SEQUENCE}{text}{END_SEQUENCE}")
