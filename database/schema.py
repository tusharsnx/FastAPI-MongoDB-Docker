# from .db import engine, Base
# from sqlalchemy import Column, Integer, String, Date, ForeignKey
# from sqlalchemy.orm import relationship

# class Users(Base):
#     __tablename__ = "users"

#     user_id = Column(String, autoincrement=True)
#     name = Column(String)
#     username = Column(String, primary_key=True, unique=True)

#     files = relationship("Files", back_populates="user")
#     # size needed to be added

#     def __repr__(self):
#         return f"name: {self.name}, username: {self.username}, file: {[file.name for file in self.files]}"
    
#     def json(self):
#         return {"user_id": self.user_id, "name": self.name, "username": self.username, "files": [file.name for file in self.files]}


# class Files(Base):
#     __tablename__ = "files"

#     file_id = Column(String, primary_key=True)
#     name = Column(String)
#     path = Column(String)
#     date_added = Column(Date)
#     username = Column(ForeignKey("users.username"), nullable=True)
    
#     user = relationship("Users", back_populates="files")

#     def __repr__(self):
#         return f"file_name: {self.name}, file_path: {self.path}, date_added: {self.date_added}"
    
#     def json(self):
#         return {"file_id": self.file_id, "file_name": self.name, "file_path": self.path, "date_added": self.date_added, "username": self.user.username}
        

    