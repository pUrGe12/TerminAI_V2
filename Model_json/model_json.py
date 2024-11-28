from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # adding the root directory to path
from address import prompts

from dotenv import load_dotenv
from pathlib import Path
import re
from supabase import create_client, Client                                        # For database adding and pulling

NAME = "model_json"

# Load the API keys from environment

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# url: str = str(os.getenv("SUPABASE_URL")).strip()
# key: str = str(os.getenv("SUPABASE_KEY")).strip()

# supabase: Client = create_client(url, key)

API_KEY = str(os.getenv("API_KEY")).strip()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def GPT_response(user_prompt):
    # history = get_history(3)
    prompt = prompts.get(NAME).strip() + f"""
                    This is the user's prompt: {user_prompt}
                """
    try:
        output = ''
        response = chat.send_message(prompt, stream=True, safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
        })
        for chunk in response:
            if chunk.text:
                output += str(chunk.text)

        # parse the output for the json and work summary etc. 

        json_list = re.findall('@@@json.*@@@', output, re.DOTALL)
        json_val = re.findall("{.*}", json_list[0].strip(), re.DOTALL)[0].strip() 			# Getting a nice normal string here
        
        return json_val

    except Exception as e:
        print(f"Error generating GPT response in model_json: {e}")
        return 'Try again'
