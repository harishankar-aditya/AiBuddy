import json
import logging
import os
import uuid
# import asyncio
import random

from typing import Any
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import Body, HTTPException
from typing import Optional

from commons.utils import convert_to_standard_types
from api.authorization.otp.send_otp import send_otp_to_email
from api.authorization.otp.validate_otp import validate_user_otp


from fastapi.responses import StreamingResponse


# router = APIRouter(prefix="")
router = APIRouter()



class OTPAuthModel(BaseModel):
    username: str
    email: str
    request_id: str = str(uuid.uuid4())
    other_info: Optional[str] = None


class ValidateOTPAuthModel(BaseModel):
    username: str
    email: str
    otp: str
    request_id: str = str(uuid.uuid4())
    other_info: Optional[str] = None


@router.post("/send-otp")
async def sendOTP(body_param: OTPAuthModel = Body(...)):
    logging.info(body_param)
    otp = str(random.randint(100000, 999999))
    response = send_otp_to_email(str(body_param.username), str(body_param.email), otp, body_param.request_id)

    if response["status_code"] == 200:
        return convert_to_standard_types(response)
    else:
        raise HTTPException(
            status_code=response["status_code"],
            detail=convert_to_standard_types(response),
        )


@router.post("/validate-otp")
async def validateOTP(body_param: ValidateOTPAuthModel = Body(...)):
    logging.info(body_param)
    response = validate_user_otp(str(body_param.username), str(body_param.email), str(body_param.otp), body_param.request_id)

    if response["status_code"] == 200:
        return convert_to_standard_types(response)
    else:
        raise HTTPException(
            status_code=response["status_code"],
            detail=convert_to_standard_types(response),
        )
    