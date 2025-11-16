from pydantic import BaseModel
from .models import Measurment_Type

class Weather_Data_Show(BaseModel):
    city : str
    weather_description : str
    temperature : float
    temperature_feels_like : float
    humidity : float
    wind_speed : float
    pressure : float

    unit_of_measurement : Measurment_Type

class Weather_Request(BaseModel):
    city : str
    temperature_measurement_in : Measurment_Type