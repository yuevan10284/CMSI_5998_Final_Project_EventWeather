function searchPlaces() {
    const query = document.getElementById('searchQuery').value;
    const location = document.getElementById('location').value;

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `query=${query}&location=${location}`
    })
    .then(response => response.json())
    .then(data => {
        displayResults(data.places);
        // Store weather data globally
        window.weatherData = data.weather;
    });
}

function displayResults(places) {
    const container = document.getElementById('results-container');
    container.innerHTML = '';
    
    places.forEach(place => {
        const card = document.createElement('div');
        card.className = 'place-card';
        card.onclick = () => showWeather(place.Name);
        card.innerHTML = `
            <h3>${place.Name}</h3>
            <p>${place.Address}</p>
            <p>${place.Category}</p>
        `;
        container.appendChild(card);
    });
}

function showWeather(placeName) {
    const modal = document.getElementById('weather-modal');
    const weather = window.weatherData;
    
    modal.innerHTML = `
        <div class="modal-content">
            <button class="close-button" onclick="closeModal()">×</button>
            <h2>Weather Forecast for ${placeName}</h2>
            <div class="forecast">
                ${weather.daily_forecast.map(day => `
                    <div class="day">
                        <h3>${day.date}</h3>
                        <div class="weather-details">
                            <p><strong>Temperature:</strong> ${day.temperature.day}°C</p>
                            <p><strong>Min:</strong> ${day.temperature.min}°C</p>
                            <p><strong>Max:</strong> ${day.temperature.max}°C</p>
                            <p><strong>Description:</strong> ${day.description}</p>
                            <p><strong>Humidity:</strong> ${day.humidity}%</p>
                            <p><strong>Wind Speed:</strong> ${day.wind_speed} m/s</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('weather-modal').style.display = 'none';
}

// Add this event listener for the Enter key
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchQuery');
    const locationInput = document.getElementById('location');
    
    function handleEnterKey(event) {
        if (event.key === 'Enter') {
            searchPlaces();
        }
    }
    
    searchInput.addEventListener('keypress', handleEnterKey);
    locationInput.addEventListener('keypress', handleEnterKey);
});
