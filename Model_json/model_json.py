from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
from address import prompts
import os
from dotenv import load_dotenv
from pathlib import Path
import re
from supabase import create_client, Client                                        # For database adding and pulling


NAME = "model_json"

# Load the API keys from environment

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

url: str = str(os.getenv("SUPABASE_URL")).strip()
key: str = str(os.getenv("SUPABASE_KEY")).strip()

supabase: Client = create_client(url, key)

API_KEY = str(os.getenv("API_KEY")).strip()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])


# def get_history(n):
#     """
#     This function queries supabase and gets the last n data points, and returns a list of the required parameters, after filtering it. This is done from version 2.

#     n -> the number of entries you want. I have kept it to be usually at 5.
#     """
#     response = supabase.table('History_v2').select("*").order('id', desc=True).limit(n).execute().data      # Take the last n
    
#     keys_to_keep = {'system_boolean', 'ex_model_function', 'user_prompt', 'ex_work_summary'}
#     filtered_data = [{key: dos[key] for key in dos if key in keys_to_keep} for dos in response]    
#     return response


def GPT_response(user_prompt):
    # history = get_history(3)
    prompt = prompts.get(NAME).strip() + f"""
                    This is the history: {history}
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
        print(f"Error generating GPT response: {e}")
        return 'Try again'
