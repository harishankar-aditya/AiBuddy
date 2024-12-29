import os
import json
import getpass
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Literal, Optional
from langchain_core.tools import tool
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

# _set_env("OPENAI_API_KEY")
# _set_env("TAVILY_API_KEY")
# _set_env("AZURE_OPENAI_API_KEY")
# _set_env("AZURE_OPENAI_ENDPOINT")
# _set_env("AZURE_OPENAI_API_VERSION")

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY", "")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION", "")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")



@tool
def get_current_date_and_time() -> str:
    """
    Retrieves the current date and time in a standardized format.  
    This tool is useful for agents to obtain the current timestamp for logging, scheduling, or time-sensitive operations.

    Args:
        *args: This parameter is included for compatibility with tool invocation patterns, but it is not used.

    Returns:
        str: The current date and time as a string in the format "YYYY-MM-DD HH:MM:SS".

    Example:
        # Example usage
        current_time = get_current_date_and_time()

        # Example response:
        # "2024-11-27 15:34:12"
    """
    print("Tool called: get_current_date_and_time")

    # Fetch the current date and time
    current_time = datetime.now()

    # Format the current date and time as "YYYY-MM-DD HH:MM:SS"
    return current_time.strftime("%Y-%m-%d %H:%M:%S")


@tool
def fetch_relevant_links(search_query, search_type: Literal["search", "news", "videos", "images", "places"] = "search"):
    """
    Fetches the latest and most relevant resource URLs based on a given search query
    using a search engine API. This tool is designed for use by agents to retrieve 
    organized web content efficiently.

    Parameters:
        search_query (str): The search query string to be sent to the search engine API.
        search_type (str): The type of search to be performed. Default is "search".


    Example:
        search_query = "latest trends in machine learning"
        results = fetch_relevant_links(search_query)
        
        Output (successful):
        [
            {
                "title": "Top Machine Learning Trends for 2024",
                "link": "https://example.com/ml-trends",
                "snippet": "Discover the top machine learning trends shaping the industry in 2024...",
                "date": "2024-11-26",
                "position": 1
            },
            ...
        ]

        Output (error):
        "Failed to retrieve the webpage. Status code: 403"
    """
    print(f"Tool invoked: fetch_relevant_links")
    print(f"Tool invoked with query: {search_query}")

    api_url = "https://google.serper.dev/search"
    payload = json.dumps({"q": search_query})
    headers = {
        'X-API-KEY': '6728d1bc815ddf1e4f47cbde162b7f0233dd9060',  # Replace with a valid API key
        'Content-Type': 'application/json'
    }

    # Send the API request
    response = requests.post(api_url, headers=headers, data=payload)

    # Handle response
    if response.status_code == 200:
        search_results = []
        response_json = response.json()
        
        for result in response_json.get('organic', []):
            result_data = {
                'title': result.get('title', ''),
                'link': result.get('link', ''),
                'snippet': result.get('snippet', ''),
                'date': result.get('date', ''),
                'position': result.get('position', 0)
            }
            search_results.append(result_data)
        
        return search_results

    else:
        return f"Failed to retrieve the webpage. Status code: {response.status_code}"



@tool
def extract_visible_text_from_webpage(url: str) -> str:
    """
    Extracts visible text content from a given webpage.  
    This tool can be used when the LLM lacks sufficient information and needs additional details from external sources. 
    The extracted text can be passed to other tools, like a search tool, for further analysis or querying.

    Args:
        url_and_title_dictionary (str): The URL and title of the webpages from which visible text content needs to be extracted in a list.

    Returns:
        Union[str, str]:
            - On success: The concatenated visible text content of the webpage, cleaned of non-visible elements like scripts and styles.

    Example:
        url = "https://example.com/article"
        text_content = extract_visible_text_from_webpage(url_and_title_dictionary)

        # Example successful response:
        # "This is the visible text extracted from the webpage. It includes headlines, paragraphs, etc."

        # Example failure response:
        # "Failed to retrieve the webpage. Status code: 404"
    """
    print("Tool called: extract_visible_text_from_webpage")
    print(f"Tool called with url: {url}")

    # Define headers to mimic a real browser for the HTTP request
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        )
    }

    try:
        # Send a GET request to the specified URL
        response = requests.get(url, headers=headers, timeout=5)

        # Check for a successful response
        if response.status_code == 200:
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove unnecessary elements (scripts, styles, meta, and links)
            for tag in soup(['script', 'style', 'meta', 'link']):
                tag.extract()

            # Extract and clean the visible text
            visible_text = soup.get_text(separator='\n', strip=True)
            cleaned_text = "\n".join(
                [line.strip() for line in visible_text.splitlines() if line.strip()]
            )

        else:
            # Handle non-200 status codes
            return f"Failed to retrieve this webpage. Status code: {response.status_code}. Fetch content from different url"
        
        return cleaned_text

    except requests.RequestException as e:
        # Handle connection errors or timeouts
        return f"An error occurred while trying to fetch the webpage: {str(e)}. Fetch content from different url"
    
