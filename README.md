# FastAPI-MongoDB-Cloud-Storage

To run on local environment, first we need to set some enviornment variables related to configuration
-
    export CLIENT_ID = your client id from the google auth server
    export CLIENT_SECRET = your client secret from the google auth server
    export DOMAIN = http://localhost:8000
    export USERNAME = your mongodb login username
    export PASS = your mongodb login pass
 
 To run the uvicorn server
 -
    uvicorn main:app

To run on heroku environment, we need to save config variable in heroku setting page
-
    CLIENT_ID: your client id from the google auth server
    CLIENT_SECRET: your client secret from the google auth server
    DOMAIN: your app domain url on heroku
    USERNAME: your mongodb login username
    PASS: your mongodb login pass
and then deploy the app
