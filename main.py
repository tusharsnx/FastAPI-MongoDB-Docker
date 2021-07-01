from fastapi import FastAPI
# from database.db import Base, engine
from routers import users, files, authorization, site
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# mouting static folder on serve for fetching static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# including all routers
app.include_router(users.router)
app.include_router(files.router)
app.include_router(authorization.router)
app.include_router(site.router)