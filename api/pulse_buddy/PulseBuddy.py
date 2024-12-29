import json
import logging
import os
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
from langchain_core.messages import AIMessageChunk, HumanMessage



from api.pulse_buddy.prompts_ import prompt
from api.pulse_buddy.tools_ import (
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
model = AzureChatOpenAI(model="gpt-4o", temperature=0.9)


tools = [ 
        fetch_relevant_links, 
        extract_visible_text_from_webpage, 
        get_current_date_and_time
        ]


def _modify_state_messages(state: AgentState):
    return prompt.invoke({"messages": state["messages"]}).to_messages()


async def pulse_multi_llm_chat(query: str, user_id: str, thread_id: str):
    # try:
    #     #DB_URI = "postgres://username@host:port/database_name""
    #     DB_URI = os.getenv("DB_URI", "")
    #     connection_kwargs = {"autocommit": True, "prepare_threshold": 0, }
    #     async with AsyncConnectionPool(
    #             conninfo=DB_URI,
    #             max_size=20,
    #             kwargs=connection_kwargs,
    #         ) as pool:
    #         checkpointer = AsyncPostgresSaver(pool)

    #         # NOTE: you need to call .setup() the first time you're using your checkpointer
    #         # await checkpointer.setup()

    #         langgraph_agent_executor = create_react_agent(
    #                                                     model, 
    #                                                     tools, 
    #                                                     state_modifier=_modify_state_messages, 
    #                                                     checkpointer=checkpointer)
    #         config = {"configurable": {"user_id": user_id, "thread_id": thread_id}}

    #         try:
    #             first = True
    #             async for msg, metadata in langgraph_agent_executor.astream({"messages": [("human", query)]}, config, stream_mode="messages"):
    #                 # print("Hari-", msg)
    #                 if msg.content and not isinstance(msg, HumanMessage):
    #                     # print(msg.content, end="", flush=True)
    #                     try:
    #                         if not msg.additional_kwargs and not msg.response_metadata and msg.id:
    #                             # a1 = msg
    #                             # a = msg['additional_kwargs']
    #                             # b = msg['response_metadata']
    #                             # c = msg['content']
    #                             # print("Hari-0", a1)
    #                             # print("Hari-1", a)
    #                             # print("Hari-2", b)
    #                             # print("Hari-3", c)
    #                             # print(msg.additional_kwargs.get("function_call"))
    #                             # break
    #                             print("hari-4")
    #                             yield msg.content
    #                     except Exception as e:
    #                         pass

    #                 # if isinstance(msg, AIMessageChunk):
    #                 #     if first:
    #                 #         gathered = msg
    #                 #         first = False
    #                 #     else:
    #                 #         gathered = gathered + msg

    #                 #     if msg.tool_call_chunks:
    #                 #         print(gathered.tool_calls)
                    
    #             # check = await checkpointer.aget(config)

            


    #         except Exception as e:
    #             logging.error(f"Got OpenAI Content violation error: {str(e)}")
    #             generic_response = f"""I'm sorry, but I cannot assist with that request. 
    #                 If there's something else you'd like help with or another topic you'd 
    #                 like to discuss, feel free to let me know! I'm here to provide information 
    #                 and support within appropriate and constructive boundaries."""
    #             response = {
    #                         "status_code": 200,
    #                         "message": "Content violation generic response",
    #                         "data": f"{generic_response}",
    #                     }
    # except Exception as e:
    #     logging.error(f"Got error in pulse_multi_llm_chat: {str(e)}")
    #     generic_response = f"""It seems something went wrong on my end, and I encountered 
    #     an internal server error. I apologize for the inconvenience. Let me try to resolve 
    #     this issue for you. Could you please provide more details or clarify your request? 
    #     'Alternatively, you can try rephrasing it, and I'll do my best to assist you!"""
    #     response = {
    #                 "status_code": 200,
    #                 "message": "Internal Server Error",
    #                 "data": f"{generic_response}",
    #             }
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
            # await checkpointer.setup()

            langgraph_agent_executor = create_react_agent(
                                                        model, 
                                                        tools, 
                                                        state_modifier=_modify_state_messages, 
                                                        checkpointer=checkpointer)
            config = {"configurable": {"user_id": user_id, "thread_id": thread_id}}
            res = await langgraph_agent_executor.ainvoke(
                {"messages": [("human", query)]}, config
            )
            response = {
                        "status_code": 200,
                        "message": "Success",
                        "data": res["messages"][-1].content,
                    }
            check = await checkpointer.aget(config)
            # print(check)
            return response
    except Exception as e:
        print(f"Error: {e}")
        response = {
                    "status_code": 500,
                    "message": "Internal Server Error",
                    "data": f"Got error: {str(e)}",
                }
        return response

# res = asyncio.run(pulse_multi_llm_chat("Hi", "sample_au_1", "buddy_1"))
# print(res['data'])
