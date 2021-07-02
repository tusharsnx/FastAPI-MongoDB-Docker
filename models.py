from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


# Request models


class UserRequestBody(BaseModel):
    name: str  = Field(..., description="Name of the user")
    username: str  = Field(..., description="Username of the user")


# Response models

# for user details
class FileModel(BaseModel):
    file_id: str = Field(..., description="File id of the file")
    name: str = Field(..., description="File name of the file")
    path: str = Field(..., description="Path of the directory where file is stored")
    size: float = Field(..., description="File size")
    date_added: date = Field(..., description="File creation date")

# for file details
class UserModel(BaseModel):
    name: str  = Field(..., description="Name of the user")
    username: str  = Field(..., description="Username of the user")
    remaining_size: float  = Field(..., description="Remaining storage space for the user")
    files: List[FileModel]  = Field(..., description="List of all files")

# for operation status
class OperationStatusModel(BaseModel):
    id: str  = Field(..., description="Id(file_id/ username) related to the operation")
    detail: str  = Field(..., description="Operation status")

# user update body
class UserUpdateModel(BaseModel):
    name: Optional[str] = Field(None, description="Name of the user")
    username: Optional[str] = Field(None, description="Username of the user")

class FileUpdateModel(BaseModel):
    name: str = Field(None, description="File name of the file")






