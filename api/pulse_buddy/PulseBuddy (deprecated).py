import warnings

warnings.warn(
    "This module is deprecated and should not be used. It may be removed in future versions.",
    DeprecationWarning,
    stacklevel=2
)

"""
This module serves as an alternative implementation for backend operations, 
intended for potential future use. While the current structure utilizes the 
`pulse_llm` module, this module offers a different approach that might better 
suit certain use cases or optimizations in the future.

**Current Status**: 
This module is not actively in use but has been designed and implemented to 
serve as a fallback or experimental setup for scenarios where `pulse_llm` 
may not fully meet requirements or where alternative approaches are needed.
"""


import os
import uuid
import tiktoken
from typing import List, Literal, Optional
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain_core.documents import Document
from langchain_core.messages import get_buffer_string
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from IPython.display import Image, display
from dotenv import load_dotenv
from api.pulse_buddy.prompts_ import prompt
from api.pulse_buddy.tools_ import (
    fetch_relevant_links,
    extract_visible_text_from_webpage, 
    fetch_current_stock_price, 
    get_current_date_and_time, 
    fetch_youtube_video_links, 
    fetch_youtube_video_transcript)
# from langchain_core.embeddings import Embeddings


def _set_env():
    load_dotenv()
    os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY", "")
    os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION", "")
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")
_set_env()

recall_vector_store = InMemoryVectorStore(AzureOpenAIEmbeddings(model="text-embedding-ada-002"))


def get_user_id(config: RunnableConfig) -> str:
    user_id = config["configurable"].get("user_id")
    if user_id is None:
        raise ValueError("User ID needs to be provided to save a memory.")

    return user_id


@tool
def save_recall_memory(memory: str, config: RunnableConfig) -> str:
    """Save memory to vectorstore for later semantic retrieval."""
    print(f"Tool called name: save_recall_memory")
    user_id = get_user_id(config)
    document = Document(
        page_content=memory, id=str(uuid.uuid4()), metadata={"user_id": user_id}
    )
    recall_vector_store.add_documents([document])
    return memory


@tool
def search_recall_memories(query: str, config: RunnableConfig) -> List[str]:
    """Search for relevant memories."""
    print(f"Tool called name: search_recall_memories")
    user_id = get_user_id(config)

    def _filter_function(doc: Document) -> bool:
        return doc.metadata.get("user_id") == user_id

    documents = recall_vector_store.similarity_search(
        query, k=3, filter=_filter_function
    )
    return [document.page_content for document in documents]


# search = TavilySearchResults(max_results=5)
# tools_name = ["save_recall_memory", "search_recall_memories", "fetch_relevant_links", "extract_visible_text_from_webpage", "fetch_current_stock_price", "get_current_date_and_time", "fetch_youtube_video_links", "fetch_youtube_video_transcript"]

class State(MessagesState):
    # add memories that will be retrieved based on the conversation context
    recall_memories: List[str]



def agent(state: State) -> State:
    """Process the current state and generate a response using the LLM.

    Args:
        state (schemas.State): The current state of the conversation.

    Returns:
        schemas.State: The updated state with the agent's response.
    """
    bound = prompt | model_with_tools
    recall_str = (
        "<recall_memory>\n" + "\n".join(state["recall_memories"]) + "\n</recall_memory>"
    )
    prediction = bound.invoke(
        {
            "messages": state["messages"],
            "recall_memories": recall_str,
        }
    )
    return {
        "messages": [prediction],
    }


def load_memories(state: State, config: RunnableConfig) -> State:
    """Load memories for the current conversation.

    Args:
        state (schemas.State): The current state of the conversation.
        config (RunnableConfig): The runtime configuration for the agent.

    Returns:
        State: The updated state with loaded memories.
    """
    convo_str = get_buffer_string(state["messages"])
    convo_str = tokenizer.decode(tokenizer.encode(convo_str)[:2048])
    recall_memories = search_recall_memories.invoke(convo_str, config)
    return {
        "recall_memories": recall_memories,
    }


def route_tools(state: State):
    """Determine whether to use tools or end the conversation based on the last message.

    Args:
        state (schemas.State): The current state of the conversation.

    Returns:
        Literal["tools", "__end__"]: The next step in the graph.
    """
    msg = state["messages"][-1]
    if msg.tool_calls:
        return "tools"

    return END

tools = [save_recall_memory, 
        search_recall_memories, 
        fetch_relevant_links, 
        extract_visible_text_from_webpage, 
        fetch_current_stock_price, 
        get_current_date_and_time, 
        fetch_youtube_video_links, 
        fetch_youtube_video_transcript]

model = AzureChatOpenAI(model="gpt-4o")
model_with_tools = model.bind_tools(tools)
tokenizer = tiktoken.encoding_for_model("gpt-4o")


def pretty_print_stream_chunk(chunk):
    for node, updates in chunk.items():
        if "messages" in updates:
            # updates["messages"][-1].pretty_print()
            updates["messages"][-1]
            return updates["messages"][-1].content
        else:
            pass
            print(f'updates: {updates}')

        print("\n")


def build_graph_workflow():
    # Create the graph and add nodes
    builder = StateGraph(State)
    builder.add_node(load_memories)
    builder.add_node(agent)
    builder.add_node("tools", ToolNode(tools))

    # Add edges to the graph
    builder.add_edge(START, "load_memories")
    builder.add_edge("load_memories", "agent")
    builder.add_conditional_edges("agent", route_tools, ["tools", END])
    builder.add_edge("tools", "agent")

    # Compile the graph
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    # display(Image(graph.get_graph().draw_mermaid_png()))
    return graph

graph = build_graph_workflow()

def pulse_multi_llm_chat(query: str, user_id: str, thread_id: str):
    try:
        # NOTE: we're specifying `user_id` to save memories for a given user
        final_response = []
        config = {"configurable": {"user_id": user_id, "thread_id": thread_id}}
        for chunk in graph.stream({"messages": [("user", query)]}, config=config):
            output = pretty_print_stream_chunk(chunk)
            final_response.append(output)
        response = {
            "status_code": 200,
            "message": "Success",
            "data": final_response[-1],
        }
    except Exception as e:
        response = {
            "status_code": 500,
            "message": "Internal Server Error",
            "data": f"Got error str(e)",
        }
    return  response
