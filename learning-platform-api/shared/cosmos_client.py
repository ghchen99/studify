from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient
import os
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT")

credential = DefaultAzureCredential()

client = CosmosClient(ENDPOINT, credential)