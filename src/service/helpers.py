from fastapi import HTTPException
import time
from datetime import datetime

from ..settings.database import redis_client
from ..settings.config import settings, logger
from .weather_tools import weather_tool
from ..models_shemas.models import  Weather_Data, Measurment_Type


def build_page_url(page: int, city_filter: str = "", date_from_filter: str = "",
                   time_from_filter: str = "", date_to_filter: str = "",
                   time_to_filter: str = "", page_size: int = 10):
    params = {"page": page}
    if city_filter:
        params["city"] = city_filter
    if date_from_filter:
        params["date_from"] = date_from_filter
    if time_from_filter:
        params["time_from"] = time_from_filter
    if date_to_filter:
        params["date_to"] = date_to_filter
    if time_to_filter:
        params["time_to"] = time_to_filter
    if page_size != 10:
        params["page_size"] = page_size

    query_string = "&".join([f"{k}={v}" for k, v in params.items() if v])

    return f"/weather-form/history?{query_string}" if query_string else "/weather-form/history"


async def Get_Weather(start_time, session, **kwargs):
    try:
        answer = redis_client.hgetall(f"{kwargs['city']}, {kwargs['temperature_measurement_in']}")
        if answer:
            weather_dict = {}
            for field_bytes, value_bytes in answer.items():
                if "." in value_bytes:
                    value_bytes = float(value_bytes)
                elif "0" <= value_bytes[0] <= "9":
                    value_bytes = int(value_bytes)
                weather_dict[field_bytes] = value_bytes

            new_weather = Weather_Data(**weather_dict, city=kwargs["city"], unit_of_measurement=kwargs["temperature_measurement_in"], served_from_cache=True)
            session.add(new_weather)
            await session.commit()

            return new_weather
    except Exception as e:
        logger.error("http_request_redis_error", extra={
            "extra_data": {
                "event_type": "http_request",
                "method": "POST",
                "path": "/weather",
                "Details": {"Redis Error" : str(e) }
            }
        })

    result = await weather_tool.get_weather(kwargs["city"])
    if result.get("error"):
        logger.error("http_request_api_error", extra={
            "extra_data": {
                "event_type": "http_request",
                "method": "POST",
                "path": "/weather",
                "status_code": 400,
                "response_time_ms": f"{time.time() - start_time} s",
                "Details": {"Api Error": str(result["error"])}
            }
        })
        raise HTTPException(status_code=400, detail=result["error"])

    try:
        temperature, feels_like = result["temperature"], result["temperature_feels_like"]
        if kwargs["temperature_measurement_in"] != Measurment_Type.Celsius:
            result["temperature"] = round(temperature * 1.8 + 32, 2)
            result["temperature_feels_like"] = round(feels_like * 1.8 + 32, 2)
        else:
            result["temperature"] = round(temperature, 2)
            result["temperature_feels_like"] = round(feels_like, 2)

        new_weather = Weather_Data(city=kwargs["city"], weather_description=result["weather_description"],
                                   temperature=result["temperature"],
                                   temperature_feels_like=result["temperature_feels_like"], pressure=result["pressure"],
                                   humidity=result["humidity"],
                                   wind_speed=result["wind_speed"], unit_of_measurement=kwargs["temperature_measurement_in"])
        session.add(new_weather)

        redis_client.hset(f"{kwargs['city']}, {kwargs['temperature_measurement_in']}", mapping=result)
        redis_client.expire(f"{kwargs['city']}, {kwargs['temperature_measurement_in']}", 300)
        await session.commit()
        return new_weather
    except Exception as e:
        logger.error("http_request_api_error", extra={
            "extra_data": {
                "event_type": "http_request",
                "method": "POST",
                "path": "/weather",
                "status_code": 500,
                "response_time_ms": f"{time.time() - start_time} s",
                "Details": f"{str(e)}"
            }
        })
        HTTPException(status_code=500, detail=str(e))

async def check_responces_limits(start_time, request_ip):
    user_ip = request_ip.headers.get("X-Forwarded-For")
    if user_ip is None:
        print("IP is not find. Use 'unknown_ip' for response")
        user_ip = "unknown_ip"
    timestamp = time.time()
    new_mas = [timik for timik in map(float, redis_client.lrange(user_ip, 0, -1)) if timik + 60 > timestamp]
    if len(new_mas) >= settings.NUMBER_OF_REQUESTS:
        logger.info("http_request_warning", extra={
            "extra_data": {
                "event_type": "http_request",
                "method": "POST",
                "path": "/weather",
                "status_code": 439,
                "response_time_ms": f"{time.time() - start_time} s",
                "Details" : "Too much responses per minute"
            }
        })
        raise HTTPException(status_code=439, detail="Sorry, but you have exceeded the number of requests per minute. Try again later.")
    else:
        redis_client.lpush(user_ip, time.time())
        redis_client.expire(user_ip, 60)
