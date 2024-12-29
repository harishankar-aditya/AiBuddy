import json
import logging
import os
import uuid
# import asyncio

from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import Body, HTTPException
from typing import Optional

from commons.utils import convert_to_standard_types
from api.pulse_video_research.PulseVideoResearch import pulse_multi_llm_chat


router = APIRouter(prefix="/chat")


class ChatModel(BaseModel):
    query: str = "Hi"
    user_id: str = str(uuid.uuid4())
    thread_id: str = str(uuid.uuid4())
    other_info: Optional[str] = None


@router.post("/")
async def chat_model(body_param: ChatModel = Body(...)):
    logging.info(body_param)
    response = await pulse_multi_llm_chat(str(body_param.query), str(body_param.user_id), str(body_param.thread_id))
    # response = asyncio.run(pulse_multi_llm_chat(str(body_param.query), str(body_param.user_id), str(body_param.thread_id)))

    if response["status_code"] == 200:
        return convert_to_standard_types(response)
    else:
        raise HTTPException(
            status_code=response["status_code"],
            detail=convert_to_standard_types(response),
        )
