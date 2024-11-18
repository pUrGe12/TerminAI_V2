from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
from address import prompts
import os
from dotenv import load_dotenv
from pathlib import Path

NAME = "model_json"

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')
API_KEY = str(os.getenv("API_KEY")).strip()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def GPT_response(user_prompt):
    prompt = prompts.get(NAME) + f"""
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
        work_summary_match = re.search(r"\$\$\$summary\s*(.*?)\s*\$\$\$", output, re.DOTALL)
        if work_summary_match:
            work_summary = work_summary_match.group(1).strip() 								# Putting an else condition, even though I am sure there must be a match
        else:
            work_summary = 'Something went wrong'

        # return (json_val, work_summary)
        return output

    except Exception as e:
        print(f"Error generating GPT response: {e}")
        return 'Try again'


if __name__ == "__main__":
	user_prompt = "Tell me about Abraham Lincoln"
	GPT_response(user_prompt)