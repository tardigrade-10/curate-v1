from fastapi import Depends, FastAPI, HTTPException
from core.api.features import htp
from core.api.features import retrieval
from core.api.features import content_development
from core.api.features import assessments

app = FastAPI(title="Curate API", description="API for the Content Extraction application.")

app.include_router(htp.router)
app.include_router(retrieval.router)
app.include_router(content_development.router)
app.include_router(assessments.router)

@app.get("/")
def root():
    return {"message": "Application running"}



