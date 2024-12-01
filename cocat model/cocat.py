# Genai imports
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai

import sys 
import os

# Necessary imports
from address import prompts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # adding the root directory to path

import re
import subprocess

# For the environment variables
from dotenv import load_dotenv
from pathlib import Path

from supabase import create_client, Client                                       # For database adding and pulling, history implementation

NAME = "concat"

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')
API_KEY = str(os.getenv("API_KEY")).strip()

genai.configure(api_key = API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def concatenate(user_prompt, final_output):
	'''
	This model takes the user's prompt and the final_output that we may or may not have to show to the user 
	and based on that generates a response that we can show to the user

	The concat model acts more like a prettifier and a response generator.

	Note that the final_output variable may or may not be empty, because if the command is something like "connect to the wifi" 
	then there is no actual output that needs to be shown, so in such cases, this model will display an output as "Connected to network 'xyz' successfully"
	'''

	init_prompt = prompts.get('concat')					# Get the init from from the address book
	
	prompt = init_prompt + f"""
			This is the user's actual prompt: {user_prompt}, \n
			This is the final output: {final_output}
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

# print(concatenate(user_prompt = 'switch on the bluetooth', final_output = ''))