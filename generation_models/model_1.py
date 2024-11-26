from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
from address import prompts

import os
from dotenv import load_dotenv

from pathlib import Path
import re
from supabase import create_client, Client                                        # For database adding and pulling

NAME = "model_1"

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

API_KEY = str(os.getenv("API_KEY")).strip()

genai.configure(api_key = API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

model_prompt = prompts.get(NAME)

def generate_command(model_prompt):
	'''We'll later incorporate history as well'''
	