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
    

@tool
def fetch_youtube_video_transcript(youtube_url: str) -> str:
    """
    Fetches the transcript of a YouTube video along with timestamps for each segment.  
    This tool is useful for extracting textual content from YouTube videos to analyze or summarize their content.

    Args:
        youtube_url (str): The URL of the YouTube video.,If provided video id, then make it youtube url.
        youtube_url = "https://www.youtube.com/watch?v=VIDEO_ID"

    Returns:
        Union[str, dict]:
            - On success: A string containing the transcript with timestamps, formatted as:
                "start_time: text"
                Example:
                "0.0: Welcome to the video."
                "5.2: Today we will discuss AI advancements."
    """
    print("Tool called: fetch_youtube_video_transcript")

    try:
        # Extract video ID from the YouTube URL
        video_id = youtube_url.split('v=')[1].split('&')[0]

        # Fetch the transcript using YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Format the transcript with timestamps
        formatted_transcript = ""
        for entry in transcript:
            start_time = entry['start']
            text = entry['text']
            formatted_transcript += f"{start_time}: {text}\n"

        return formatted_transcript

    except Exception as e:
        # Return an error message in case of an exception
        return {"error": f"Failed to fetch the transcript: {str(e)}"}


@tool
def fetch_youtube_video_links(search_query: str):
    """
    Fetches YouTube video links relevant to a given search query.  
    This tool searches Google for YouTube video links and retrieves the top results along with their titles.  
    It can be used to provide video sources that might help users with their queries.

    Args:
        search_query (str): The search query for which YouTube video links are to be retrieved.

    Returns:
        Union[List[Dict[str, str]], Dict[str, str]]:
            - On success: A list of dictionaries, each containing:
                - "title" (str): The title of the video.
                - "source" (str): The URL to the YouTube video.

    Example:
        search_query = "Python programming tutorials"
        videos = fetch_youtube_video_links(search_query)
    """
    print("Tool called: fetch_youtube_video_links")

    # Construct the Google search URL
    url = f"https://www.google.com/search?q=site:https://www.youtube.com/ {search_query}"

    # Define headers to mimic a real browser request
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
    }

    try:
        # Send a GET request to fetch search results
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, "html.parser")

            # Locate and extract video links and titles
            results = []
            link_counter = 0
            for link_element in soup.select("span[jscontroller='msmzHf'] a[jsname='UWckNb']"):
                # Extract the href (link)
                link = link_element['href'] if link_element else None

                # Extract the title from the nested h3 tag
                title_element = link_element.select_one("h3.LC20lb.MBeuO.DKV0Md")
                title = title_element.text if title_element else None

                # Add to results if both title and link are found
                if link and title:
                    results.append({
                        "title": title,
                        "source": link
                    })
                    link_counter += 1
                    if link_counter >= 3:  # Limit to the top 3 results
                        break

            return results if results else {"message": "No results found"}

        else:
            return {"message": "Got some error! Check internet for latest data"}

    except Exception as e:
        # Return an error message in case of exceptions
        return {"message": f"An error occurred: {str(e)}"}
    