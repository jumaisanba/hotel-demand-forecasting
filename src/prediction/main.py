from fastapi import FastAPI

from prediction.api.routers.forecast import router as forecast_router
from prediction.api.routers.model_info import router as model_info_router
from prediction.api.routers.predict import router as predict_router
from prediction.api.routers.training import router as training_router
from shared.errors import register_error_handlers, setup_openapi_with_errors

app = FastAPI(title="Prediction Service API")

register_error_handlers(app)
setup_openapi_with_errors(app)

app.include_router(predict_router, prefix="/predict", tags=["predict"])
app.include_router(forecast_router, prefix="/forecast", tags=["forecast"])
app.include_router(training_router, prefix="/models", tags=["models"])
app.include_router(model_info_router, prefix="/models", tags=["models"])


@app.get("/")
def root():
    return {"message": "Prediction Service is running"}