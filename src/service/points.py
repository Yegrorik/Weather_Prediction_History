from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse
from sqlalchemy import select
from fastapi.templating import Jinja2Templates

import os
from datetime import datetime
from datetime import date
import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from typing import Annotated
import math

import csv
import io

from ..settings.database import get_session
from ..models_shemas.models import Weather_Data
from .helpers import build_page_url, Get_Weather, check_responces_limits
from ..models_shemas.shemas import Weather_Data_Show, Weather_Request
from ..settings.config import logger

weather_router = APIRouter()

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
templates_dir = os.path.join(parent_dir, "templates")

templates = Jinja2Templates(directory=templates_dir)



@weather_router.post("/weather", response_model=Weather_Data_Show)
async def get_weather(request : Weather_Request, request_ip : Request, session : Annotated[AsyncSession, Depends(get_session)]):
    logger.info("http_request_start", extra={
        "extra_data": {
            "event_type": "http_request",
            "method": "POST",
            "path": "/weather",
            "client_ip": f"{request_ip.headers.get('X-Forwarded-For')}",
            "query_params": {"city": f"{request.city}",
                             "temperature_measurement_in" : f"{request.temperature_measurement_in}"
                             },
        }
    })
    start_time = time.time()
    await check_responces_limits(start_time, request_ip)
    city = request.city.lower()
    city = city[:1].upper() + city[1:]
    result = await Get_Weather(start_time=start_time, session=session, city=city, temperature_measurement_in=request.temperature_measurement_in)

    logger.info("http_request_success", extra={
        "extra_data": {
            "event_type": "http_request",
            "method": "POST",
            "path": "/weather",
            "status_code": 200,
            "response_time_ms": f"{time.time()-start_time} s",
        }
    })

    return result


@weather_router.get("/export-csv")
async def export_csv(session : Annotated[AsyncSession, Depends(get_session)], request : Request,
                     city : str = "", date_from : str = "", date_to : str = ""):
    logger.info("http_request_start", extra={
        "extra_data": {
            "event_type": "http_request",
            "method": "GET",
            "path": "/export-csv",
            "client_ip": f"{request.headers.get('X-Forwarded-For')}",
            "query_params": {"city": city,
                             "date_from" : date_from,
                             "date_to" : date_to
                             },
        }
    })
    start_time = time.time()

    try:
        query = select(Weather_Data)
        if city:
            query = query.where(Weather_Data.city.like(f"{city}%"))
        if date_from != "None":
            date_from = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
            query = query.where(Weather_Data.created_at >= date_from)


        if date_to != "None":
            date_to = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
            query = query.where(Weather_Data.created_at <= date_to)

        results = await session.execute(query.order_by(Weather_Data.created_at.desc()))
        history_records = results.scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['City', 'Temperature', 'Temperature Feels Like', 'Description', 'Humidity', 'Wind Speed', 'Pressure', 'Time of request'])

        for data in history_records:
            writer.writerow([
                data.city,
                f"{data.temperature} {data.unit_of_measurement}",
                f"{data.temperature_feels_like} {data.unit_of_measurement}",
                data.weather_description,
                f"{data.humidity} %",
                f"{data.wind_speed} км/ч",
                f"{data.pressure} hPa",
                data.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        csv_content = output.getvalue()

        logger.info("http_request_success", extra={
            "extra_data": {
                "event_type": "http_request",
                "method": "GET",
                "path": "/export-csv",
                "status_code": 200,
                "response_time_ms": f"{time.time() - start_time} s",
            }
        })

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=weather_history.csv"}
        )
    except Exception as e:
        logger.error("http_request_error", extra={
            "extra_data": {
                "event_type": "http_request",
                "method": "GET",
                "path": "/export-csv",
                "response_time_ms": f"{time.time() - start_time} s",
                "Details" : str(e)
            }
        })


@weather_router.get("/", response_class=HTMLResponse)
async def weather_form_page(request: Request):
    return templates.TemplateResponse("weather.html", {
        "request": request
    })

@weather_router.get("/weather-form/history", response_class=HTMLResponse)
async def get_weather_history(
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
    page: int = 1,
    city: str = "",
    date_from: str = "",
    time_from: str = "",
    date_to: str = "",
    time_to: str = "",
    page_size: int = 10,
):
    logger.info("http_request_start", extra={
        "extra_data": {
            "event_type": "http_request",
            "method": "GET",
            "client_ip": f"{request.headers.get('X-Forwarded-For')}",
            "path": f"{request.url}",
        }
    })
    start_time = time.time()
    try:
        query = select(Weather_Data)
        if city:
            city = city.lower()
            city = city[:1].upper() + city[1:]
            query = query.where(Weather_Data.city.like(f"{city}%"))

        date_time_from = None
        if date_from:
            try:
                if time_from:
                    date_time_from = datetime.strptime(f"{date_from} {time_from}","%Y-%m-%d %H:%M:%S")
                else:
                    date_time_from = datetime.strptime(date_from,"%Y-%m-%d")

                query = query.where(Weather_Data.created_at >= date_time_from)
            except ValueError as e:
                print(f"⚠️ Неверный формат date_from/time_from: {date_from} {time_from} - {e}")
        else:
            if time_from:
                date_from = date.today()
                date_time_from = datetime.strptime(f"{date_from} {time_from}","%Y-%m-%d %H:%M:%S")
                query = query.where(Weather_Data.created_at >= date_time_from)


        date_time_to = None
        if date_to:
            try:
                if time_to:
                    date_time_to = datetime.strptime(f"{date_to} {time_to}","%Y-%m-%d %H:%M:%S")
                else:
                    date_time_to = datetime.strptime(date_to,"%Y-%m-%d")
                query = query.where(Weather_Data.created_at <= date_time_to)
            except ValueError as e:
                print(f"⚠️ Неверный формат date_from/time_from: {date_to} {time_to} - {e}")
        else:
            if time_to:
                date_to = date.today()
                date_time_to = datetime.strptime(f"{date_to} {time_to}","%Y-%m-%d %H:%M:%S")
                query = query.where(Weather_Data.created_at <= date_time_to)


        resukt = await session.execute(query.order_by(Weather_Data.created_at.desc()))
        history_records = resukt.scalars().all()

        total_items = len(history_records)
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0

        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages

        offset = (page - 1) * page_size
        current_page_data = history_records[offset:offset + page_size]

        pagination_info = {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "page_size": page_size,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "start_item": offset + 1,
            "end_item": min(offset + page_size, total_items)
        }

        logger.info("http_request_success", extra={
            "extra_data": {
                "event_type": "http_request",
                "method": "GET",
                "path": f"{request.url}",
                "status_code": 200,
                "response_time_ms": f"{time.time() - start_time} s",
            }
        })

        return templates.TemplateResponse("Jon.html", {
            "request": request,
            "queries": current_page_data,
            "pagination": pagination_info,
            "city_filter": city,
            "date_from_filter": date_from,
            "time_from_filter": time_from,
            "date_to_filter": date_to,
            "time_to_filter": time_to,
            "available_page_sizes": [5, 10, 20, 50],
            "build_page_url": build_page_url,
            "all_date_from": date_time_from,
            "all_date_to": date_time_to
        })
    except Exception as e:
        logger.error("http_request_error", extra={
            "extra_data": {
                "event_type": "http_request",
                "method": "GET",
                "path": f"{request.url}",
                "response_time_ms": f"{time.time() - start_time} s",
                "Details": str(e)
            }
        })