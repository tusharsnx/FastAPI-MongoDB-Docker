from models import OperationStatusModel,  FileModel, FileUpdateModel
from fastapi import APIRouter
from fastapi import BackgroundTasks, File, UploadFile, HTTPException
from database.crud import read_file, delete_after_read_file, create_file, read_user, update_file
import utils
import urllib.parse
from tempfile import SpooledTemporaryFile

router = APIRouter(tags=["files"], prefix="/api/files")

# dir for saving user files
DIR = "uploaded"

# file limit in mb
LIMIT = 5

# creates new file
@router.post("/{username}", response_model=OperationStatusModel)
async def add_file(username: str,  task: BackgroundTasks, file: UploadFile = File(...)):
    '''Recieves file from the client and stores in the server
        - username : username for the user
        - file : file to upload
    '''
    # checking if user exists
    user = await read_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    # checking if file size is less than limit
    temp_file = SpooledTemporaryFile(max_size=1024*1024)
    file_size: float = 0
    for chunk in file.file:
        file_size += len(chunk)/(1024*1024)
        if file_size>LIMIT or file_size>user["remaining_size"]:
            raise HTTPException(413, detail="file size exceeded")
        temp_file.write(chunk)
    
    # sometimes filename recieved are enconded with url-like format
    decoded_file_name = urllib.parse.unquote(file.filename)
    # 'file' attributes are filename, file(file-like object)
    file_id = await create_file(file_name=decoded_file_name, username=username, size=float(file_size), dir="uploaded")      
    # creating background task to save received file
    task.add_task(utils.file_save, file=temp_file,  path=f"{DIR}/{file_id}")
    
    return {"id": decoded_file_name, "detail": "operation successful"}

# return file detail
@router.get("/{username}/{file_id}", response_model=FileModel)
async def get_file(file_id: str, username: str):
    file = await read_file(file_id=file_id, username=username)
    if file is None:
        raise HTTPException(status_code=404, detail="file not found")
    else:
        return file


# deletes a file
@router.delete("/{username}/{file_id}", response_model=OperationStatusModel)
async def remove_file(file_id: str, username: str,  tasks: BackgroundTasks):
    # read file content to get path
    file = await read_file(file_id=file_id, username=username)
    if file is None:
        raise HTTPException(status_code=404, detail="user's file not found") 

    # delete by passing file doc
    await delete_after_read_file(file)
    tasks.add_task(utils.file_delete, path=file["path"])
    return {"id": file["file_id"], "detail": "operation successful"}


# update file detail(filename)
@router.put("/{username}/{file_id}", response_model=OperationStatusModel)
async def update_file_detail(username: str, file_id: str, update_data: FileUpdateModel):
    update_data = update_data.dict(exclude_unset=True)
    result = await update_file(username=username, file_id=file_id, data=update_data)
    if result:
        return {"id": file_id, "detail": "Operation successful"}
    else: 
        raise HTTPException(404, detail="file not found")
