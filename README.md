# YourDrive (Cloud Storage)

#### Demo: [railway.app](https://fastapi-mongodb-docker-production.up.railway.app)

## Local Run

To run it locally, first we need to set some environments.

```sh
export CLIENT_ID = <client-id from the Google Identity Platform> 
export CLIENT_SECRET = <client-secret from the Google Identity Platform>
export DOMAIN = http://localhost:8000
export USERNAME = <mongodb username>
export PASS = <mongodb password>
```

This project is using poetry for dependency management.

Install the dependencies:

```sh
poetry install
poetry shell
```
    
Then run the uvicorn server:
    
```sh
cd app
uvicorn main:app
```


Then run the uvicorn server:

```sh
cd app
uvicorn main:app
```

## Remote deployment

Apply the enviroments in the project settings. 

```sh
CLIENT_ID = <client-id from the Google Identity Platform> 
CLIENT_SECRET = <client-secret from the Google Identity Platform>
DOMAIN: <domain(url) given by the Cloud provider> 
USERNAME = <mongodb username>
PASS: <mongodb pass>
```

Deploy the app.