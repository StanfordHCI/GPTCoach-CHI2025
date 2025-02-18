# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from firebase import FirebaseManager
from api import data_endpoints, gpt_endpoints, firebase_endpoints

async def on_startup():
    firebase_manager = FirebaseManager()
    firebase_manager.initialize_firebase_app()

async def on_shutdown():
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup()
    yield
    await on_shutdown()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    # ADD YOUR PRODUCTION URL HERE
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(data_endpoints.router)
app.include_router(gpt_endpoints.router)
app.include_router(firebase_endpoints.router)
