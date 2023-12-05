from fastapi import Depends, FastAPI, HTTPException
from core.api.features import htp
from core.api.features import retrieval


app = FastAPI(title="Curate API", description="API for the Content Extraction application.")

app.include_router(htp.router)
app.include_router(retrieval.router)

@app.get("/")
def root():
    return {"message": "Application running"}



