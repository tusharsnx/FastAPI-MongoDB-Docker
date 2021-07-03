from fastapi import APIRouter, BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import Response, RedirectResponse, HTMLResponse
from jose import jwt
from uuid import uuid4
import aiohttp
import asyncio
import yaml
import os

# loading config for authorization
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
SCOPE = "openid email profile"
DOMAIN = os.environ["DOMAIN"]


class OAuth2Handler:
    '''
    class for handling all authorization related operations including verfying and decoding jwt
    '''

    def __init__(self, client_secret, client_id, redirect_url, scope):

        self.client_secret = client_secret
        self.client_id = client_id
        self.token_endpoint = None
        self.redirect_url = redirect_url
        self.scope = scope
        self.authorization_endpoint = None
        self.jwks_uri = None
        self.issuer = None
        self.verification_options ={
                'verify_sub': False,
                'verify_at_hash': False,
            }

        loop = asyncio.get_event_loop()
        loop.create_task(self.load_urls())

    # fetches auth, token granting url and issuer name
    async def load_urls(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://accounts.google.com/.well-known/openid-configuration") as response:
                response = await response.json()
                self.jwks_uri = response.get("jwks_uri")
                self.authorization_endpoint = response.get("authorization_endpoint")
                self.token_endpoint = response.get("token_endpoint")
                self.issuer = response.get("issuer")

        
    # creates payloads for exchanging code for id_token
    def token_request_payload(self, code):
        token_request_payload = {
            "grant_type": "authorization_code", "code": code, "client_id": self.client_id, 
            "client_secret": self.client_secret, "redirect_uri": self.redirect_url
        }
        return token_request_payload

    # authentication url with all required query parameter
    def auth_server_url(self):
        url = self.authorization_endpoint+"?"+f"client_id={self.client_id}&redirect_uri={self.redirect_url}&response_type=code&scope={self.scope}&nonce={uuid4()}"
        return url

    def encode_token(self):
        pass

    # verify the token and if valid returns the payload
    async def decode_token(self, token):
        key = None
        async with aiohttp.ClientSession() as session:
            async with session.get(self.jwks_uri) as response:
                key = await response.json()
        try:
            data = jwt.decode(token=token, key=key, algorithms="RS256", options=self.verification_options, 
                issuer=self.issuer, audience=self.client_id
                )
        except:
            return None
        return data

    # fetches access_token and id_token from the auth server
    async def get_token_details(self, code):
        token = None

        # aiohttp for async access_token request
        async with aiohttp.ClientSession() as session:
            payload = self.token_request_payload(code)
            async with session.post(self.token_endpoint, data=payload) as response:
                token = await response.json()
        return token


auth = OAuth2Handler(
    client_secret=CLIENT_SECRET, 
    client_id=CLIENT_ID, 
    redirect_url=DOMAIN+"/auth/callback", 
    scope=SCOPE
    )


router = APIRouter(prefix="/auth", tags=["authorization"], include_in_schema=False)


# redirects to auth server if not logged in
@router.get("/login", response_class=HTMLResponse)
async def login(response: Response):
    return RedirectResponse(url=auth.auth_server_url())      


# callback url which receives code and create new user in the website
@router.get("/callback")
async def callback(request: Request, response: Response, task: BackgroundTasks):
    
    # getting the code from query parameter
    code = request.query_params.get("code")

    # exchanging code for token
    token_details = await auth.get_token_details(code)
    decoded_data = await auth.decode_token(token_details["id_token"])

    # creating new user in the database if not exist
    task.add_task(create_new_user, name=decoded_data["name"], username=decoded_data["email"])

    # redirecting to main page
    response = RedirectResponse(url=f"{DOMAIN}/home")

    response.set_cookie(key="token", value=token_details["id_token"], httponly=True)
    return response


# route for logging out which deletes the cookie from the browser
@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url=f"{DOMAIN}/home")
    response.delete_cookie("token")
    return response

# background task for creating new user if not exist already
async def create_new_user(name, username):

    # checking if user exists
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{DOMAIN}/api/users/{username}") as resp:
            data = await resp.json()

            if resp.status!=200:
                # user does not exists
                data = {"username": username, "name": name}
                await session.post(f"{DOMAIN}/api/users", json=data)