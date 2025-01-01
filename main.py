import os
import json
import logging


from fastapi import FastAPI, Request, status, File, UploadFile, Form, Cookie, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()


from api.authorization import endpoints as AuthorizationEndpoints
from api.pulse_buddy import endpoints as PulseBuddyChatEndpoints
from api.pulse_video_research import endpoints as PulseVideoResearchChatEndpoints
from api.authorization.otp.validate_token import validate_access_token
from config import variables


if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)


app = FastAPI()
app.mount("/frontend/static", StaticFiles(directory="frontend/static"), name="frontend/static")
templates = Jinja2Templates(directory="frontend/templates")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/", response_class=HTMLResponse)
async def main(request: Request, access_token: str = Cookie(None), response: Response = Response()):
    if access_token:
        return RedirectResponse(url="/profile")
    else:
        return templates.TemplateResponse("home.html", {"request": request})
    # return templates.TemplateResponse("home.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, access_token: str = Cookie(None), response: Response = Response()):
    if access_token:
        return RedirectResponse(url="/profile")
    else:
        return templates.TemplateResponse("home.html", {"request": request})
    # return templates.TemplateResponse("home.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, access_token: str = Cookie(None), response: Response = Response()):
    if access_token:
        token_response = validate_access_token(access_token)
        if token_response["data"] is not None:
            return templates.TemplateResponse("chatbot.html", {"request": request, "username": token_response["data"][0]["username"]})
        else:
            response = templates.TemplateResponse("home.html", {"request": request})
            response.delete_cookie(key="access_token")
            return response
    else:
        return RedirectResponse(url="/home")
    # return templates.TemplateResponse("chatbot.html", {"request": request})


@app.post("/logout", response_class=HTMLResponse)
async def logout(request: Request, response: Response, access_token: str = Cookie(None)):
    response = templates.TemplateResponse("home.html", {"request": request})
    if access_token is not None:
        response.delete_cookie(key="access_token")
    return response


app.include_router(
    AuthorizationEndpoints.router,
    prefix="/api/auth",
    tags=["Authorization APIs"],
)


app.include_router(
    PulseBuddyChatEndpoints.router,
    prefix="/api/pulse-buddy",
    tags=["PulseBuddy Chat APIs"],
)


app.include_router(
    PulseVideoResearchChatEndpoints.router,
    prefix="/api/pulse-video-research",
    tags=["PulseVideoResearch Chat APIs"],
)





@app.get('/favicon.ico')
async def favicon():
    file_name = "favicon.ico"
    file_path = os.path.join(app.root_path, "frontend/static", file_name)
    # file_path = "abg-mvps-backend/frontend/static/favicon.ico"
    return FileResponse(path=file_path, headers={"Content-Disposition": "attachment; filename=" + file_name})



# Define a health check route without any path parameters
@app.get("/api/health-check/", status_code=status.HTTP_200_OK)
async def health_check(request: Request):
    return JSONResponse(content={"status": variables.SERVER_ALIVE_MESSAGE})



# # ERROR 404 Default page
# @app.get("/{path:path}")
# def catch_all(path: str):
#     return HTMLResponse(content=open("frontend/templates/not-found.html").read(), status_code=404)


# if __name__ == '__main__':
#     print("HELLO! RUNNING ON 7001")
#     uvicorn.run("main:app", host="0.0.0.0", port=7001, reload=True)
