
from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv("C:/Users/Lenovo Legion 5/Documents/Python/MCQ_generatorV1/APIs/groq.env")

api = os.getenv("groq_api_key")

client = OpenAI(
    api_key=api,
    base_url="https://api.groq.com/openai/v1",
)

response = client.responses.create(
    input="What is 4+1",
    model="openai/gpt-oss-20b",
)
