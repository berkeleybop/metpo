import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file or environment variables.")
else:
    try:
        # Attempt a simple API call (e.g., list models)
        openai.api_key = api_key
        response = openai.models.list()
        print("Successfully connected to OpenAI API. Key is valid.")
        # print(response)
    except openai.AuthenticationError:
        print("Error: OpenAI API key is invalid or unauthorized.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
