from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pintrigue_backend.api.endpoints import auth, pin, user, comment

app = FastAPI()

origins = [
    'https://localhost:3000',
    'http://localhost:3000',
    'http://localhost:3000/'
]

app.include_router(auth.router)
app.include_router(pin.router)
app.include_router(user.router)
app.include_router(comment.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)