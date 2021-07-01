from models import OperationStatusModel,  FileModel
from fastapi import APIRouter
from typing import List
from fastapi import BackgroundTasks, File, UploadFile, HTTPException, Form
from database.crud import read_file, delete_file, create_file, read_user
import utils
from fastapi.security import OAuth2PasswordBearer
import urllib.parse

router = APIRouter(tags=["files"], prefix="/api/files")
auth = OAuth2PasswordBearer(tokenUrl="token")

# dir for saving user files
DIR = "uploaded"

@router.post("/{username}", response_model=OperationStatusModel)
async def add_file(username: str,  task: BackgroundTasks, file: UploadFile = File(...), size: str = Form(...)):

    # checking if user exists
    user = await read_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    # sometimes filename recieved are enconded in url-like format
    decoded_file_name = urllib.parse.unquote(file.filename)

    # 'file' attributes are filename, file(file-like object)
    file_id = await create_file(file_name=decoded_file_name, username=username, size=float(size), dir="uploaded")
       
    # creating background task to save received file
    task.add_task(utils.file_save, file = file,  path=f"{DIR}/{file_id}")
    return {"id": decoded_file_name, "detail": "operation successful"}


@router.get("/{username}/{file_id}", response_model=FileModel)
async def get_file(file_id: str, username: str):
    file = await read_file(file_id=file_id, username=username)
    if file is None:
        raise HTTPException(status_code=404, detail="file not found")
    else:
        return file

@router.delete("/{username}/{file_id}", response_model=OperationStatusModel)
async def remove_file(file_id: str, tasks: BackgroundTasks, username: str):

    response = await delete_file(file_id=file_id, username=username)
    if not response:
        raise HTTPException(404, detail="user's file not found")
    tasks.add_task(utils.file_delete, path=response.path)
    return {"detail": "operation successful"}
