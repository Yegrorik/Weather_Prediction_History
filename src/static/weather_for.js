const form = document.getElementById('weatherForm');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const successResult = document.getElementById('successResult');
const errorResult = document.getElementById('errorResult');
const weatherInfo = document.getElementById('weatherInfo');
const errorMessage = document.getElementById('errorMessage');

form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const city = document.getElementById('city').value.trim();
    const temperature_measurement_in = document.getElementById('temperature_measurement_in').value;
    
    if (!city) {
        showError('Enter city name');
        return;
    }
    
    await getWeather(city, temperature_measurement_in);
});

async function getWeather(city, temperature_measurement_in) {
    showLoading();
    hideResults();
    
    try {
        const response = await fetch('/weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                city: city,
                temperature_measurement_in: temperature_measurement_in
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Server error');
        }
        
        displayWeather(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function displayWeather(weatherData) {
    const unit = document.getElementById('temperature_measurement_in').value;
    
    weatherInfo.innerHTML = `
        <div class="weather-item">
            <strong>🏙️ City:</strong>
            <span>${weatherData.city || 'Not specified'}</span>
        </div>
        <div class="weather-item">
            <strong>🌡️ Temperature:</strong>
            <span>${weatherData.temperature || 0} ${unit}</span>
        </div>
        <div class="weather-item">
            <strong>🤔 Feels like:</strong>
            <span>${weatherData.temperature_feels_like || 0} ${unit}</span>
        </div>
        <div class="weather-item">
            <strong>📝 Description:</strong>
            <span>${weatherData.weather_description || 'No description'}</span>
        </div>
        <div class="weather-item">
            <strong>💧 Humidity:</strong>
            <span>${weatherData.humidity || 0}%</span>
        </div>
        <div class="weather-item">
            <strong>💨 Wind speed:</strong>
            <span>${weatherData.wind_speed || 0} km/h</span>
        </div>
        <div class="weather-item">
            <strong>📊 Pressure:</strong>
            <span>${weatherData.pressure || 0} hPa</span>
        </div>
        ${weatherData.served_from_cache ? `
        <div class="weather-item">
            <strong>⚡ Status:</strong>
            <span>Data from cache</span>
        </div>
        ` : ''}
    `;
    
    showSuccess();
}

function showLoading() {
    loading.style.display = 'block';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Loading...';
}

function hideLoading() {
    loading.style.display = 'none';
    submitBtn.disabled = false;
    submitBtn.textContent = '🔍 Get Weather';
}

function showSuccess() {
    successResult.style.display = 'block';
    errorResult.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    successResult.style.display = 'none';
    errorResult.style.display = 'block';
}

function hideResults() {
    successResult.style.display = 'none';
    errorResult.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('city').focus();
});