from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.api import auth
from offer.api import offers_api
from chat.api_ex import chat


app = FastAPI()
app.include_router(auth)
app.include_router(offers_api)
app.include_router(chat)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:3000', 'http://localhost:3000', 'http://localhost:63342'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
