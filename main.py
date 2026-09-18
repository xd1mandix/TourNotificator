from bot import _main_
from fastapi import FastAPI

app = FastAPI()

_main_()

@app.get("/")
def root():
    return {"message": "bot is up"}
 

