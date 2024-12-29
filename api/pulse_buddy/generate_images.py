# from openai import OpenAI
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY", "")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION", "")

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("OPENAI_API_VERSION"),
)

response = client.images.generate(
    model="dall-e-3",
    prompt="a white siamese cat",
    size="1024x1024",
    quality="standard",
    style="natural",
    n=1,
)

print(response.data[0].url)