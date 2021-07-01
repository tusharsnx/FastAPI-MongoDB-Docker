from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Request models


class UserRequestBody(BaseModel):
    name: str
    username: str


# Response models

# for user details
class FileModel(BaseModel):
    file_id: str
    name: str
    path: str
    size: float
    date_added: datetime

# for file details
class UserModel(BaseModel):
    name: str
    username: str
    remaining_size: float
    files: List[FileModel]

# for operation status
class OperationStatusModel(BaseModel):
    id: str
    detail: str

# user update body
class UserUpdateModel(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None






