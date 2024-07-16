from fastapi import FastAPI
from workou_api.routers import api_router

app = FastAPI(title='WorkoutApi')
app.include_router(api_router)



@app.get("/")
def home():
    return "API está no ar"