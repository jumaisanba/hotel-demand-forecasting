from sqlalchemy import Column, Integer, String, Boolean
from auth_service.db import Base

class Hotel(Base):
    __tablename__ = "hotel"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    is_city_hotel = Column(Boolean, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
