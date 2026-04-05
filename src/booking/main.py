from fastapi import FastAPI

from booking.api.routers.booking_router import router as booking_router
from booking.api.routers.forecast_router import router as prediction_router
from booking.api.routers.hotels import router as hotels_router
from shared.errors import register_error_handlers, setup_openapi_with_errors

app = FastAPI(title="Booking Service API")

register_error_handlers(app)
setup_openapi_with_errors(app)

app.include_router(booking_router, prefix="/booking")
app.include_router(prediction_router, prefix="/forecast")
app.include_router(hotels_router, prefix="/hotel")


@app.get("/")
def root():
    return {"message": "Booking Service is running"}
