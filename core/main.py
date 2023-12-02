from fastapi import Depends, FastAPI, HTTPException
from core.api import htp

app = FastAPI()

app.include_router(htp.router)

@app.get("/")
def root():
    return {"message": "Application running"}



