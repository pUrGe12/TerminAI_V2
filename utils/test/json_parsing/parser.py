import json

from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # adding the root directory to path
from address import prompts

from dotenv import load_dotenv
from pathlib import Path

sample_prompt = """connect to wifi "motog73" and start wireshark recording"""

test_js = """ 
[
	{ 
		"operation": "connect_wifi", 
			"order": 0, 
			"parameters": { "wifi_name": "motog73" } 
	},

	{ 
		"operation": "start_wireshark_recording", 
			"order": 1, 
			"parameters": {}  
	} 
] """


operations = json.loads(test_js)

sorted_operations = sorted(operations, key=lambda x: x['order']) 			# in general we can assume it will give us the sorted output only

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')
API_KEY = str(os.getenv("API_KEY")).strip()

def categorise(json):
	
	genai.configure(api_key=API_KEY)
	model = genai.GenerativeModel('gemini-pro')
	chat = model.start_chat(history=[])
	
	parser_prompt = prompts.get('parser')

	output = ""

	try:
		output = ''
		response = chat.send_message(parser_prompt + f"{json}", stream=True, safety_settings={
				HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
				HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
				HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
				HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
		})
		for chunk in response:
			if chunk.text:
				output += str(chunk.text)

		return output

	except Exception as e:
		print(f"Error generating GPT response: {e}")
		return 'Try again'

categorised = categorise(sorted_operations)

json.loads(categorised)