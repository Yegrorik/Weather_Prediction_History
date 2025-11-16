# Weather Application

A modern weather web application built with FastAPI, PostgreSQL, Redis, and Docker. Get current weather data for any city with caching, rate limiting, and historical data tracking.

## Features

- 🌤️ Get current weather for any city
- 💾 PostgreSQL database for storing request history
- ⚡ Redis caching for improved performance
- 🔒 Rate limiting (30 requests per minute)
- 📊 Weather history with filtering and pagination
- 📁 CSV export functionality
- 🐳 Docker containerization
- 🌍 Cloudflare tunnel for public access

## Quick Start

### Prerequisites

- Docker
- Docker Compose
- OpenWeatherMap API key ([Get one here](https://openweathermap.org/api))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Yegrorik/Weather_Prediction_History.git
   cd Weather_Prediction_History

2. Create environment file
    ```bash
    copy .env.sample .env

3. Update the following variables in .env:

    WEATHER_API_KEY: Your OpenWeatherMap API key
    DB_PASSWORD: Your PostgreSQL password
    DB_USER: user data base
    WEATHER_API_KEY: Your Api Key from OpenWeatherMap
    DB_NAME: Name of your Data Base

5. Launch with Docker
    ```bash
    docker-compose build --no-cache

6. Run with Docker Compose
    ```bash
    docker compose up

7. Access the application
Open localhost:8000 in your browser
The application is ready to use!

Need a public URL?
Check the logs for Cloudflare tunnel URL:
   ```bash
   docker compose logs cloudflared
