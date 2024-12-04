# Genai imports
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai

import sys 
import os

# Necessary imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # adding the root directory to path
from address import sanitizer_prompt

# For the environment variables
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')
API_KEY = str(os.getenv("API_KEY")).strip()

genai.configure(api_key = API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def santize(command):
	'''
	This takes the command and tells whether its extremely harmful to the system or not

	Input:
	Bash or PowerShell commands

	output: 
	If harmful then --> output: "Harmful: <reason>"
	If not harmful then --> output: "safe"
	'''

	init_prompt = sanitizer_prompt					# Get the init from from the address book
	
	prompt = init_prompt + f"""
			This is the command: {command}
		"""

	try:
		output = ''
		response = chat.send_message(prompt, 
			stream=True, 
			safety_settings={
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