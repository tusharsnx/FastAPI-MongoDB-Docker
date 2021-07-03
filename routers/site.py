# from main import DOMAIN
from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from models import UserModel, UserRequestBody
from .authorization import auth
from typing import Union
import utils
import aiohttp
import yaml
import os

# loading domain url
with open('config.yaml', 'r') as f:
    config = yaml.load(f)

DOMAIN = os.environ["DOMAIN"]
INNER_DOMAIN = DOMAIN

router = APIRouter(default_response_class=HTMLResponse, include_in_schema=False)
template = Jinja2Templates(directory="templates")

# dependency for getting user info before serving user
async def get_current_user(request: Request):
    token = request.cookies.get("token")
    # cookie contains token
    if token:
        data = await auth.decode_token(token)
        # token is still valid
        if data:
            return UserRequestBody(name=data["name"], username=data["email"])
        else:
            return None
    else:
        return None

# route for home page
@router.get("/")
@router.get("/home", name="home")
async def index(request: Request, user: UserRequestBody = Depends(get_current_user)):
    if user is None:
        return template.TemplateResponse("home.html", {"request": request, "user": None})
    else:
        return template.TemplateResponse("home.html", {"request": request, "user": {"name": user.name, "username": user.username}})

# route for downloading files
@router.get("/download/{file_id}")
async def file_download(file_id: str, request: Request, user: UserRequestBody = Depends(get_current_user)):
    if user is None:
        return RedirectResponse(url=f"{DOMAIN}/auth/login")

    # fetches file details from the database using api call
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{INNER_DOMAIN}/api/files/{user.username}/{file_id}") as resp:
            file = await resp.json()

            # file details not available
            if resp.status!=200:
                return template.TemplateResponse("file_not_found.html", {"request": request})

        # if details exist but file does not exists in the directory
        if not utils.file_exists(file["path"]):
            await session.delete(f"{INNER_DOMAIN}/api/files/{user.username}/{file_id}")
            return template.TemplateResponse("file_not_found.html", {"request": request})

    # return file, if exists
    return FileResponse(file["path"], filename=file["name"])
    

# route for file dashboard page
@router.get("/dashboard", name="dashboard")
async def dashboard(request: Request, user: UserRequestBody = Depends(get_current_user)):
    '''
    shows all user's files in a html page.
    '''
    if user is None:
        return RedirectResponse(url=f"{DOMAIN}/auth/login")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{INNER_DOMAIN}/api/users/{user.username}") as resp:
            user_info = await resp.json()
    if user_info:
        files = [{"filename": file["name"], "date_added": file["date_added"], "file_id": file["file_id"], "size": file["size"]} for file in user_info["files"]]
        user_dict = {"name": user_info["name"], "username": user_info["username"], "remaining_size": round(user_info["remaining_size"], 2)}
    return template.TemplateResponse("dashboard.html",{"request": request, "user": user_dict, "user_files": files})

# route for uploading files
@router.post("/upload", response_class=JSONResponse)
async def upload(task: BackgroundTasks, user: UserRequestBody = Depends(get_current_user), file: UploadFile = File(...)):
    if user is None: 
        return RedirectResponse(url=f"{DOMAIN}/auth/login")

    response = await upload_file(file=file, username=user.username)
    if response==1:
        return {"detail": "File uploaded successfully"}
    if response==0:
        raise HTTPException(404, detail="User not found")
    if response==-1:
        raise HTTPException(413, detail="File size exceeded")


@router.get("/delete/{file_id}", response_class=HTMLResponse)
async def delete(request: Request, file_id: str, user: UserRequestBody = Depends(get_current_user)):
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{INNER_DOMAIN}/api/files/{user.username}/{file_id}") as resp:
            if resp.status!=200:
                return template.TemplateResponse("file_not_found.html", {"request": Request})

    return RedirectResponse(url=f"{DOMAIN}/dashboard")

# background task for saving files
async def upload_file(file: UploadFile, username: str):
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData(quote_fields=False)
        data.add_field('file', file.file.read(), filename=file.filename)
        async with session.post(f"{INNER_DOMAIN}/api/files/{username}", data=data) as resp:
            if resp.status==200:
                return 1
            elif resp.status==404:
                return 0
            else:
                return -1
    

