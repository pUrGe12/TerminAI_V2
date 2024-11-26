# Genai imports
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai

# Necessary imports
from address import prompts
import re
import subprocess

# For the environment variables
import os
from dotenv import load_dotenv
from pathlib import Path

# For database adding and pulling
from supabase import create_client, Client                                       

NAME = "model_2"

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')
API_KEY = str(os.getenv("API_KEY")).strip()

genai.configure(api_key = API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def generate_command(user_prompt):
	'''We'll later incorporate history as well'''
	
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

	except Exception as e:
		print(f"Error generating GPT response: {e}")
		return 'Try again'

	return output

def execute(generated_command):
	""" 
	We must ensure that the command generated will not harm the computer 
	-- Implement santisation here!
	"""

	try:
		command = generated_command
		output = subprocess.run(command, shell=True, text=True, check = True, capture_output=True)
		return output.stdout

	except Exception as e:
		return f"you've hit {e}"


# cmd = generate_command('write a 100 word essay on abhraham lincon and store that in a file in the desktop')
# print(cmd)
# print(execute(cmd))
