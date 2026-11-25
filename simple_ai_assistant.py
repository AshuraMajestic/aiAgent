# standard library imports
import os

# Third-party imports
from openai import OpenAI
from dotenv import load_dotenv
from types import SimpleNamespace

# Local modules
from tools import TOOLS, run_tool
from utilities.utilities import log,build_tool_calls_payload
from memory import list_chats,load_chat,save_chat
  

load_dotenv() #by default looks for .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages = []
chat_file_path = None  # Initialize chat_file_path to None

# Safety limit: the max number of model rounds for ONE user question
MAX_STEPS = 5

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a helpful, humble assistant for NIMBUS DYNAMICS PVT. LTD. "
        "Answer general questions (programming, science, advice) from your own knowledge. "
        "Use get_current_time, get_city_weather and get_user_city only for the current time, "
        "the weather, or the user's city. "
        "For ANY question about NIMBUS DYNAMICS PVT. LTD. policies, benefits, leave, medical cover, HR, hiring, "
        "tech processes, incident reports or travel expenses, "
        "you MUST first call search_knowledge_base. "
        "Answer company questions ONLY from the text that search_knowledge_base returns. "
        "Do not use outside knowledge for company facts. "
        "After the answer, cite the source like (leave_policy.txt #3). "
        "If the returned text does not contain the answer, say exactly: "
        "I could not find this in the knowledge base. "
        "Keep answers under 100 words."
    )
}
messages.append(SYSTEM_MESSAGE)

def stream_chat(history):
    stream = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=history,
            tools=TOOLS,
            stream=True,
        )

    full_response = ""
    calls = {}
    label_printed = False

    #Streaming started
    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            #1. Content Streaming : Do we have message (content) from the LLM
            if delta.content:
                if not label_printed:
                    print("🤖 Assistant: ", end="", flush=True)
                    label_printed = True
                print(delta.content, end="", flush=True)
                full_response += delta.content

            #2. Tool Calls
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
        print("\n {Stopped By You}")
        calls = {}
    
    if label_printed:
        print()  # Move to the next line after the assistant's response

    calls_list = []
    for key in sorted(calls):
        calls_list.append(calls[key])
    
    return full_response, calls_list


existing_chats = list_chats()
if existing_chats:
    last_chat = existing_chats[0]
    answer=input(f"Do you want to continue the last chat '{last_chat['title']}'? (y/n): ")
    
    if answer.lower()=="y":
        data=load_chat(last_chat["path"])
        if data is not None:
            messages=[SYSTEM_MESSAGE]+data["messages"]
            chat_file_path = last_chat["path"]
            print((f"Continuing chat '{last_chat['title']}' with {len(data['messages'])} messages."))
            
def show_chats(chats):
    chat_number=1
    for chat in chats:
        title = chat['title']
        count=chat['count']
        updated=chat['updated']
        print(f"{chat_number}. {title} ({count} messages, last updated: {updated})")
        chat_number += 1

# Chat loop starts from here
while True:

    user_input = input("\nAshura: ")
    
    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    command=user_input.strip().lower()
    
    if command=="/new":
        messages=[SYSTEM_MESSAGE]
        print("Started a new chat., The old one is still saved.")
        continue
    
    if command=='/chats':
        chats=list_chats()
        if chats:
            show_chats(chats)
        else:
            print("No previous chats found.")
        continue
    if command=='/resume':
        chats=list_chats()
        if not chats:
            print("No previous chats found.")
            continue
        
        show_chats(chats)
        chat_number=input("Enter the chat number to resume ( Press Enter for none): ")
        chat_number=chat_number.strip()
        
        if not chat_number.isdigit() or not (1 <= int(chat_number) <= len(chats)):
            print("Invalid chat number. Continuing with the current chat.")
            continue
        
        chat = chats[int(chat_number) - 1]
        data = load_chat(chat["path"])
        
        if data is None:
            print(f"Failed to load chat '{chat['title']}'. Continuing with the current chat.")
            continue
        messages = [SYSTEM_MESSAGE] + data["messages"]
        chat_file_path = chat["path"]
        print(f"Resumed chat '{chat['title']}' with {len(data['messages'])} messages.")
        continue
        
    
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Chained Tool Calling
    for step in range(MAX_STEPS):
        full_response, tool_calls = stream_chat(messages)

        #msg = response.choices[0].message

        if not tool_calls:
            break

        log(f"Step {step + 1}: model requested {len(tool_calls)} tool calls")

        messages.append({
            "role": "assistant",
            "content": full_response or None,
            "tool_calls": build_tool_calls_payload(tool_calls)
        })

        for tool_call in tool_calls:
            result = run_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id" : tool_call.id,
                "content" : str(result),
            })

    else:
        # Ran out of steps: The model never gave the final answer
        fallback = "Sorry, I could not finish this within the step limit."
        messages.append({
            "role": "assistant",
            "content": fallback
        })
        print("🤖 Assistant: " + fallback)
        chat_file_path = save_chat(chat_file_path, messages[1:])
        continue

    messages.append({
            "role": "assistant",
            "content": full_response
    })
    chat_file_path = save_chat(chat_file_path, messages[1:])