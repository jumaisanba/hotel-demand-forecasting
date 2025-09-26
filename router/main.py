import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.routers import auth_router, data_interface_router, prediction_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Router Service", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(data_interface_router.router, prefix="/data", tags=["Data Interface"])
app.include_router(prediction_router.router, prefix="/prediction", tags=["Prediction"])


@app.get("/")
def root():
    return {"message": "Router Service is running"}
