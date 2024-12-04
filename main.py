from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class Message(BaseModel):
    text: str

@app.get("/")
def index():
    return HTMLResponse(content=open("index.html", "r", encoding="utf-8").read())
