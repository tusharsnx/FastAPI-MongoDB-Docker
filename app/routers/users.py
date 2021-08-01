from fastapi import APIRouter
from starlette.background import BackgroundTasks
from typing import List
from models import UserRequestBody, UserModel, FileModel, OperationStatusModel, UserUpdateModel
from fastapi import HTTPException
from database.crud import delete_user, get_files, read_user, read_users, create_user, update_user
import utils

router = APIRouter(tags=["users"], prefix="/api/users")

# returns list of user
@router.get("/", response_model=List[UserModel])
async def users_list(limit: int = 10):
    return await read_users(limit=limit)

# returns user details for provided username
@router.get("/{username}", response_model=UserModel)
async def user_detail(username: str):
    user_detail = await read_user(username)
    if user_detail is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user_detail


@router.get("/{username}/files", response_model=List[FileModel])
async def get_files_list(username: str):
    file_list = await get_files(username)
    if file_list is None:
        raise HTTPException(status_code=404, detail = "user not found")
    else:
        return file_list

# creates new user
@router.post("/", response_model=OperationStatusModel)
async def add_user(user: UserRequestBody):
    response = await create_user(name=user.name, username=user.username)
    if not response:
        return {"id": user.username, "detail": "user already exists"}
    return {"id": user.username, "detail": "Operation Succesful"}

# deletes user
@router.delete("/{username}", response_model=OperationStatusModel)
async def remove_user(username: str, task: BackgroundTasks):
    user = await read_user(username)
    if user:

        #adding background task to delete files from the  directory
        for file in user["files"]:
            task.add_task(utils.file_delete, path=file["path"])

        response = await delete_user(username=username)
        if response:
            return {"id": username, "detail": "operation successful"}

    raise HTTPException(404, detail="user not found")

#update user detail(user's name)
@router.put("/{username}")
async def update_user_detail(username: str, update_data: UserUpdateModel):
    update_data = update_data.dict(exclude_unset=True)
    response = await update_user(username=username, data=update_data)
    if response: 
        return {"id": username, "detail": "operation successful"}
    else: 
        raise HTTPException(404, detail="user not found")