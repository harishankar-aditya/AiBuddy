# from openai import OpenAI
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY", "")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION", "")


def generateImage(prompt):

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("OPENAI_API_VERSION"),
    )




    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        style="natural",
        n=1,
    )
    return response.data[0].url
    print(response.data[0].url)




prompt = f"""
Generate a comedy meme of a person with a large head and a small body with some written joke or line of text.
"""

print(generateImage(prompt))
