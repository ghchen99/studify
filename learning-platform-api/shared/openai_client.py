import os
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-5.1")
api_key = os.getenv("AZURE_OPENAI_KEY")

# Correct format: base_url should end with /openai/v1/
# Remove trailing slash from endpoint if it exists
endpoint = endpoint.rstrip('/')

client = OpenAI(
    base_url=f"{endpoint}/openai/v1/",
    api_key=api_key,
    default_headers={"api-key": api_key}
)

# Pydantic models for structured response
class Sightseeing(BaseModel):
    name: str
    description: str
    category: str

class ParisResponse(BaseModel):
    sights: List[Sightseeing]

try:
    # Use the parse() method
    completion = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a helpful travel assistant."},
            {"role": "user", "content": "Give me 5 must-see places in Paris."}
        ],
        response_format=ParisResponse,
    )

    # Access the parsed response
    parsed = completion.choices[0].message.parsed

    # Print results
    for sight in parsed.sights:
        print(f"{sight.name} ({sight.category}): {sight.description}")
        
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting steps:")
    print("1. Verify your deployment name is correct")
    print("2. Check if your model supports structured outputs")
    print("3. Ensure your Azure OpenAI resource has the correct API version")