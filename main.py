from bot import _main_
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    _main_()
    return {"message": "bot is up"}
 


