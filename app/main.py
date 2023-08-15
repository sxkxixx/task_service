from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.api import auth
from offer.api import offers_api

app = FastAPI()
app.include_router(auth)
app.include_router(offers_api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.on_event('startup')
async def startup():
    pass


@app.on_event('shutdown')
async def shutdown():
    pass
