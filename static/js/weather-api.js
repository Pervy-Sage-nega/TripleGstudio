// Weather API integration for Site Diary
document.addEventListener('DOMContentLoaded', function() {
    const weatherButton = document.getElementById('fetch-weather-btn');
    const refreshWeatherButton = document.getElementById('refreshWeather');
    const projectSelect = document.getElementById('id_project');
    const locationInput = document.getElementById('siteLocation') || document.getElementById('id_location');
    
    // Handle weather fetch button
    if (weatherButton) {
        weatherButton.addEventListener('click', function(e) {
            e.preventDefault();
            fetchWeatherData();
        });
    }
    
    // Handle refresh weather button
    if (refreshWeatherButton) {
        refreshWeatherButton.addEventListener('click', function(e) {
            e.preventDefault();
            fetchWeatherData();
        });
    }
    
    // Auto-fetch weather when project changes
    if (projectSelect) {
        projectSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption.value) {
                // Get project location from data attribute or fetch it
                const projectLocation = selectedOption.getAttribute('data-location');
                if (projectLocation && locationInput) {
                    locationInput.value = projectLocation;
                    // Auto-fetch weather for the project location
                    setTimeout(() => fetchWeatherData(), 500);
                }
            }
        });
    }
    
    function fetchWeatherData() {
        const location = locationInput ? locationInput.value : 'London'; // Default location
        const button = weatherButton || refreshWeatherButton;
        const originalText = button ? button.textContent : '';
        
        // Show loading state
        if (button) {
            button.textContent = 'Fetching Weather...';
            button.disabled = true;
        }
        
        // Show loading in weather displays
        updateWeatherDisplay('morning', { loading: true });
        updateWeatherDisplay('afternoon', { loading: true });
        
        // Make AJAX request to Django backend
        fetch('/diary/api/weather/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `location=${encodeURIComponent(location)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fillWeatherFields(data.data);
                updateWeatherDisplay('morning', data.data);
                updateWeatherDisplay('afternoon', data.data);
                showMessage(`Weather data fetched for ${data.data.location}, ${data.data.country}!`, 'success');
            } else {
                showMessage('Error: ' + data.error, 'error');
                updateWeatherDisplay('morning', { error: data.error });
                updateWeatherDisplay('afternoon', { error: data.error });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Failed to fetch weather data', 'error');
            updateWeatherDisplay('morning', { error: 'Failed to fetch weather data' });
            updateWeatherDisplay('afternoon', { error: 'Failed to fetch weather data' });
        })
        .finally(() => {
            // Reset button state
            if (button) {
                button.textContent = originalText;
                button.disabled = false;
            }
        });
    }
    
    function fillWeatherFields(weatherData) {
        // Map weather condition
        const conditionMapping = {
            'clear': 'sunny',
            'clouds': 'cloudy',
            'rain': 'rainy',
            'drizzle': 'rainy',
            'thunderstorm': 'stormy',
            'snow': 'snowy',
            'mist': 'foggy',
            'fog': 'foggy',
            'haze': 'foggy'
        };
        
        // Fill form fields
        const weatherConditionSelect = document.getElementById('id_weather_condition');
        if (weatherConditionSelect) {
            const mappedCondition = conditionMapping[weatherData.condition] || 'cloudy';
            weatherConditionSelect.value = mappedCondition;
        }
        
        const tempHighInput = document.getElementById('id_temperature_high');
        if (tempHighInput) {
            tempHighInput.value = weatherData.temperature_high || weatherData.temperature;
        }
        
        const tempLowInput = document.getElementById('id_temperature_low');
        if (tempLowInput) {
            tempLowInput.value = weatherData.temperature_low || (weatherData.temperature - 5);
        }
        
        const humidityInput = document.getElementById('id_humidity');
        if (humidityInput) {
            humidityInput.value = weatherData.humidity;
        }
        
        const windSpeedInput = document.getElementById('id_wind_speed');
        if (windSpeedInput) {
            windSpeedInput.value = weatherData.wind_speed;
        }
        
        // Show weather description
        showMessage(`Weather: ${weatherData.description}`, 'info');
    }
    
    function updateWeatherDisplay(period, weatherData) {
        const prefix = period === 'morning' ? 'morning' : 'afternoon';
        
        // Update weather icon
        const iconElement = document.getElementById(`${prefix}WeatherIcon`);
        if (iconElement) {
            if (weatherData.loading) {
                iconElement.innerHTML = '<i class="fas fa-sync fa-spin"></i>';
            } else if (weatherData.error) {
                iconElement.innerHTML = '<i class="fas fa-exclamation-triangle text-danger"></i>';
            } else {
                const weatherIcon = getWeatherIcon(weatherData.condition);
                iconElement.innerHTML = `<i class="${weatherIcon}"></i>`;
            }
        }
        
        // Update weather description
        const descElement = document.getElementById(`${prefix}WeatherDesc`);
        if (descElement) {
            if (weatherData.loading) {
                descElement.textContent = 'Loading...';
            } else if (weatherData.error) {
                descElement.textContent = 'Error loading weather';
            } else {
                descElement.textContent = weatherData.description || 'Unknown';
            }
        }
        
        // Update temperature
        const tempElement = document.getElementById(`${prefix}Temp`);
        if (tempElement) {
            if (weatherData.loading) {
                tempElement.textContent = '--';
            } else if (weatherData.error) {
                tempElement.textContent = '--';
            } else {
                tempElement.textContent = weatherData.temperature || '--';
            }
        }
        
        // Update wind speed
        const windElement = document.getElementById(`${prefix}Wind`);
        if (windElement) {
            if (weatherData.loading) {
                windElement.textContent = '--';
            } else if (weatherData.error) {
                windElement.textContent = '--';
            } else {
                windElement.textContent = weatherData.wind_speed || '--';
            }
        }
        
        // Update humidity
        const humidityElement = document.getElementById(`${prefix}Humidity`);
        if (humidityElement) {
            if (weatherData.loading) {
                humidityElement.textContent = '--';
            } else if (weatherData.error) {
                humidityElement.textContent = '--';
            } else {
                humidityElement.textContent = weatherData.humidity || '--';
            }
        }
        
        // Update precipitation (if available)
        const precipElement = document.getElementById(`${prefix}Precipitation`);
        if (precipElement) {
            if (weatherData.loading) {
                precipElement.textContent = '--';
            } else if (weatherData.error) {
                precipElement.textContent = '--';
            } else {
                precipElement.textContent = weatherData.precipitation || '0';
            }
        }
    }
    
    function getWeatherIcon(condition) {
        const iconMapping = {
            'clear': 'fas fa-sun text-warning',
            'clouds': 'fas fa-cloud text-secondary',
            'rain': 'fas fa-cloud-rain text-primary',
            'drizzle': 'fas fa-cloud-drizzle text-info',
            'thunderstorm': 'fas fa-bolt text-warning',
            'snow': 'fas fa-snowflake text-light',
            'mist': 'fas fa-smog text-secondary',
            'fog': 'fas fa-smog text-secondary',
            'haze': 'fas fa-smog text-secondary'
        };
        return iconMapping[condition] || 'fas fa-cloud text-secondary';
    }
    
    function showMessage(message, type) {
        // Create or update message element
        let messageDiv = document.getElementById('weather-message');
        if (!messageDiv) {
            messageDiv = document.createElement('div');
            messageDiv.id = 'weather-message';
            messageDiv.className = 'alert alert-info mt-2';
            weatherButton.parentNode.appendChild(messageDiv);
        }
        
        messageDiv.textContent = message;
        messageDiv.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} mt-2`;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (messageDiv) {
                messageDiv.remove();
            }
        }, 5000);
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
