import os
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-5.1")
subscription_key = os.getenv("AZURE_OPENAI_KEY")

api_version = "2025-03-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

# Define structured response with Pydantic
class Sightseeing(BaseModel):
    name: str
    description: str
    category: str

class ParisResponse(BaseModel):
    sights: List[Sightseeing]

# Prompt for structured JSON output
prompt = """
You are a helpful travel assistant. Provide 5 must-see places in Paris in JSON format like this:
{
  "sights": [
    {
      "name": "...",
      "description": "...",
      "category": "museum | landmark | park | neighborhood | other"
    }
  ]
}
"""

response = client.responses.create(
    model=deployment,
    input=prompt,
    max_output_tokens=1000
)

# Use Pydantic v2 method to validate JSON string
parsed = ParisResponse.model_validate_json(response.output_text)

# Print nicely
for sight in parsed.sights:
    print(f"{sight.name} ({sight.category}): {sight.description}")
