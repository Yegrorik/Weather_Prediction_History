import aiohttp

from ..settings.config import settings

class WeatherTool:
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.BASE_WEATHER_URL

    async def get_weather(self, city : str):
        url = f"{self.base_url}/weather?q={city}&appid={self.api_key}&units=metric&lang=ru"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        main = data["main"]
                        return {
                            "weather_description" : data["weather"][0]["description"],
                            "temperature" : main["temp"],
                            "temperature_feels_like" : main["feels_like"],
                            "pressure" : main["pressure"],
                            "humidity" : main["humidity"],
                            "wind_speed" : round(data["wind"]["speed"] * (1000 / 360), 2)
                        }
                    else:
                        error_data = await response.json()
                        return {"error" :  f"Error: {error_data.get('message', 'City not found')}"}
        except Exception as e:
            return {"error" : f"Request Error: {str(e)}"}

weather_tool = WeatherTool()

