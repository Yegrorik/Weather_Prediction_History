from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, Boolean
from sqlalchemy import func
import enum

from ..settings.database import Base

class Measurment_Type(str, enum.Enum):
    Fahrenheit = "°F"
    Celsius = "°C"

class Weather_Data(Base):
    __tablename__ = "weather_data"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    city : Mapped[str]
    weather_description : Mapped[Text] = mapped_column(Text, nullable=False)
    temperature : Mapped[float]
    temperature_feels_like : Mapped[float]
    humidity : Mapped[float]
    wind_speed : Mapped[float]
    pressure : Mapped[int] = mapped_column(Integer, server_default="1000", nullable=False)

    unit_of_measurement: Mapped[str] = mapped_column(
        default=Measurment_Type.Celsius,
        server_default=Measurment_Type.Celsius,
        nullable=False
    )

    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    served_from_cache : Mapped[bool] = mapped_column(Boolean, default = False, server_default="false", nullable=False)