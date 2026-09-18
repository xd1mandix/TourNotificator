from bot import _main_
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "bot is up"}

_main_()
