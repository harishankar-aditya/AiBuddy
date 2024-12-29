import json
import logging
import os
import re
import uuid
# import asyncio

from datetime import datetime
from typing import Optional
from langgraph.prebuilt import create_react_agent
# from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
# from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv


from api.pulse_video_research.prompts_ import prompt
from api.pulse_video_research.tools_ import (
        fetch_youtube_video_links,
        fetch_youtube_video_transcript,
        fetch_relevant_links,
        extract_visible_text_from_webpage, 
        get_current_date_and_time)


def _set_env():
    load_dotenv()
    os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY", "")
    os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION", "")
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")
_set_env()
model = AzureChatOpenAI(model="gpt-4o")


tools = [ 
        fetch_youtube_video_links,
        fetch_youtube_video_transcript,
        fetch_relevant_links, 
        extract_visible_text_from_webpage, 
        get_current_date_and_time
        ]


def _modify_state_messages(state: AgentState):
    return prompt.invoke({"messages": state["messages"]}).to_messages()


def extract_youtube_links(markdown_content):
    # Regular expression to match YouTube links
    youtube_regex = r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+"

    # Extracting all YouTube links
    youtube_links = re.findall(youtube_regex, markdown_content)

    # Returning the list of YouTube links
    return youtube_links


async def pulse_multi_llm_chat(query: str, user_id: str, thread_id: str):
    try:
        #DB_URI = "postgres://username@host:port/database_name""
        DB_URI = os.getenv("DB_URI", "")
        connection_kwargs = {"autocommit": True, "prepare_threshold": 0, }
        async with AsyncConnectionPool(
                conninfo=DB_URI,
                max_size=20,
                kwargs=connection_kwargs,
            ) as pool:
            checkpointer = AsyncPostgresSaver(pool)

            # NOTE: you need to call .setup() the first time you're using your checkpointer
            await checkpointer.setup()

            langgraph_agent_executor = create_react_agent(
                                                        model, 
                                                        tools, 
                                                        state_modifier=_modify_state_messages, 
                                                        checkpointer=checkpointer)
            config = {"configurable": {"user_id": user_id, "thread_id": thread_id}}
            res = await langgraph_agent_executor.ainvoke(
                {"messages": [("human", query)]}, config
            )
            youtube_links = extract_youtube_links(res["messages"][-1].content)

            response = {
                        "status_code": 200,
                        "message": "Success",
                        "data": res["messages"][-1].content,
                        "youtube_links": youtube_links
                    }
            check = await checkpointer.aget(config)
            # print(check)
            return response
    except Exception as e:
        response = {
                    "status_code": 500,
                    "message": "Internal Server Error",
                    "data": f"Got error: {str(e)}",
                    "youtube_links": None
                }
        return response

# res = asyncio.run(pulse_multi_llm_chat("Hi", "sample_au_1", "buddy_1"))
# print(res['data'])
