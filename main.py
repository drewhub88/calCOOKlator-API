from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers.recipes import router as recipes_router

app = FastAPI(title="calCooklator", version="1.0.0")

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(recipes_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "Culinary Scaler & Cost API is running. Visit /docs to try it."}