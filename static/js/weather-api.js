// Weather API Integration for Site Diary
const WEATHER_API_KEY = '0c461dd2b831a59146501773674950cd';
const WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather';

document.addEventListener('DOMContentLoaded', function() {
    initializeWeatherSystem();
});

function initializeWeatherSystem() {
    // Initialize flatpickr for time inputs
    initializeTimePickers();
    
    // Set up event listeners
    setupEventListeners();
    
    // Auto-fetch weather if location is available
    autoFetchWeatherOnLoad();
}

function initializeTimePickers() {
    const timeInputs = ['morningStart', 'morningEnd', 'afternoonStart', 'afternoonEnd'];
    
    timeInputs.forEach(inputId => {
        const element = document.getElementById(inputId);
        if (element) {
            flatpickr(element, {
                enableTime: true,
                noCalendar: true,
                dateFormat: "H:i",
                time_24hr: true,
                defaultHour: getDefaultHour(inputId),
                defaultMinute: 0
            });
        }
    });
}

function getDefaultHour(inputId) {
    const defaults = {
        'morningStart': 8,
        'morningEnd': 12,
        'afternoonStart': 13,
        'afternoonEnd': 17
    };
    return defaults[inputId] || 8;
}

function setupEventListeners() {
    // Fetch weather button
    const fetchBtn = document.getElementById('fetch-weather-btn');
    if (fetchBtn) {
        fetchBtn.addEventListener('click', fetchWeatherData);
    }
    
    // Project name change listener
    const projectSelect = document.getElementById('id_project');
    if (projectSelect) {
        projectSelect.addEventListener('change', updateProjectLocation);
    }
    
    // Auto-fetch when time inputs change
    const timeInputs = ['morningStart', 'morningEnd', 'afternoonStart', 'afternoonEnd'];
    timeInputs.forEach(inputId => {
        const element = document.getElementById(inputId);
        if (element) {
            element.addEventListener('change', debounce(autoFetchWeatherForShifts, 1000));
        }
    });
}

function autoFetchWeatherOnLoad() {
    const locationInput = document.getElementById('siteLocation');
    if (locationInput && locationInput.value.trim()) {
        // Automatically fetch weather immediately on page load
        fetchWeatherData();
    }
}

function autoFetchWeatherForShifts() {
    const location = document.getElementById('siteLocation')?.value.trim();
    const morningStart = document.getElementById('morningStart')?.value;
    const afternoonStart = document.getElementById('afternoonStart')?.value;
    
    if (location && (morningStart || afternoonStart)) {
        fetchWeatherData();
    }
}

async function fetchWeatherData() {
    const locationInput = document.getElementById('siteLocation');
    const fetchBtn = document.getElementById('fetch-weather-btn');
    
    if (!locationInput || !locationInput.value.trim()) {
        showWeatherError('Location not available for weather data');
        return;
    }
    
    const fullLocation = locationInput.value.trim();
    
    // Show loading state
    if (fetchBtn) {
        fetchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching...';
        fetchBtn.disabled = true;
    }
    updateWeatherLoadingState(true);
    
    // Try multiple location formats in order of preference
    const locationVariants = getLocationVariants(fullLocation);
    
    let weatherData = null;
    let lastError = null;
    
    for (const location of locationVariants) {
        try {
            const response = await fetch(`${WEATHER_API_URL}?q=${encodeURIComponent(location)}&appid=${WEATHER_API_KEY}&units=metric`);
            
            if (response.ok) {
                weatherData = await response.json();
                console.log(`Weather found for: ${location}`);
                break;
            } else {
                console.log(`Weather not found for: ${location} (${response.status})`);
            }
        } catch (error) {
            console.log(`Weather API error for ${location}:`, error);
            lastError = error;
        }
    }
    
    if (weatherData) {
        updateWeatherDisplay(weatherData);
        updateFormFields(weatherData);
    } else {
        console.error('All weather location variants failed:', lastError);
        showWeatherError('Weather data not available for this location. Please enter manually.');
        enableManualInput();
    }
    
    // Reset loading state
    if (fetchBtn) {
        fetchBtn.innerHTML = '<i class="fas fa-cloud-sun"></i> Fetch Weather';
        fetchBtn.disabled = false;
    }
    updateWeatherLoadingState(false);
}

function updateWeatherDisplay(data) {
    const temp = Math.round(data.main.temp);
    const condition = data.weather[0].description;
    const humidity = data.main.humidity;
    const windSpeed = Math.round(data.wind.speed * 3.6); // Convert m/s to km/h
    const iconCode = data.weather[0].icon;
    
    // Update morning weather display
    updateWeatherSection('morning', {
        temp,
        condition,
        humidity,
        windSpeed,
        iconCode
    });
    
    // Update afternoon weather display (same data for current weather)
    updateWeatherSection('afternoon', {
        temp,
        condition,
        humidity,
        windSpeed,
        iconCode
    });
}

function updateWeatherSection(period, weatherData) {
    const { temp, condition, humidity, windSpeed, iconCode } = weatherData;
    
    // Update temperature
    const tempElement = document.getElementById(`${period}Temp`);
    if (tempElement) tempElement.textContent = temp;
    
    // Update description
    const descElement = document.getElementById(`${period}WeatherDesc`);
    if (descElement) descElement.textContent = capitalizeFirst(condition);
    
    // Update humidity
    const humidityElement = document.getElementById(`${period}Humidity`);
    if (humidityElement) humidityElement.textContent = humidity;
    
    // Update wind speed
    const windElement = document.getElementById(`${period}Wind`);
    if (windElement) windElement.textContent = windSpeed;
    
    // Update weather icon
    const iconElement = document.getElementById(`${period}WeatherIcon`);
    if (iconElement) {
        iconElement.innerHTML = getWeatherIcon(iconCode);
    }
}

function updateFormFields(data) {
    // Update Django form fields
    const tempHigh = document.getElementById('id_temperature_high');
    const tempLow = document.getElementById('id_temperature_low');
    const humidity = document.getElementById('id_humidity');
    const windSpeed = document.getElementById('id_wind_speed');
    const weatherCondition = document.getElementById('id_weather_condition');
    
    if (tempHigh) tempHigh.value = Math.round(data.main.temp_max);
    if (tempLow) tempLow.value = Math.round(data.main.temp_min);
    if (humidity) humidity.value = data.main.humidity;
    if (windSpeed) windSpeed.value = Math.round(data.wind.speed * 3.6);
    
    // Set weather condition dropdown
    if (weatherCondition) {
        const condition = mapWeatherCondition(data.weather[0].main);
        weatherCondition.value = condition;
    }
}

function mapWeatherCondition(apiCondition) {
    const conditionMap = {
        'Clear': 'sunny',
        'Clouds': 'cloudy',
        'Rain': 'rainy',
        'Drizzle': 'rainy',
        'Thunderstorm': 'stormy',
        'Snow': 'snowy',
        'Mist': 'foggy',
        'Fog': 'foggy',
        'Haze': 'hazy'
    };
    
    return conditionMap[apiCondition] || 'partly_cloudy';
}

function getWeatherIcon(iconCode) {
    const iconMap = {
        '01d': '<i class="fas fa-sun text-warning"></i>',
        '01n': '<i class="fas fa-moon text-info"></i>',
        '02d': '<i class="fas fa-cloud-sun text-warning"></i>',
        '02n': '<i class="fas fa-cloud-moon text-info"></i>',
        '03d': '<i class="fas fa-cloud text-secondary"></i>',
        '03n': '<i class="fas fa-cloud text-secondary"></i>',
        '04d': '<i class="fas fa-cloud text-dark"></i>',
        '04n': '<i class="fas fa-cloud text-dark"></i>',
        '09d': '<i class="fas fa-cloud-rain text-primary"></i>',
        '09n': '<i class="fas fa-cloud-rain text-primary"></i>',
        '10d': '<i class="fas fa-cloud-sun-rain text-primary"></i>',
        '10n': '<i class="fas fa-cloud-moon-rain text-primary"></i>',
        '11d': '<i class="fas fa-bolt text-warning"></i>',
        '11n': '<i class="fas fa-bolt text-warning"></i>',
        '13d': '<i class="fas fa-snowflake text-info"></i>',
        '13n': '<i class="fas fa-snowflake text-info"></i>',
        '50d': '<i class="fas fa-smog text-secondary"></i>',
        '50n': '<i class="fas fa-smog text-secondary"></i>'
    };
    
    return iconMap[iconCode] || '<i class="fas fa-cloud text-secondary"></i>';
}

function showWeatherError(message) {
    // Update morning weather display with error
    const morningDesc = document.getElementById('morningWeatherDesc');
    const afternoonDesc = document.getElementById('afternoonWeatherDesc');
    
    if (morningDesc) morningDesc.textContent = message;
    if (afternoonDesc) afternoonDesc.textContent = message;
    
    // Show error styling
    const weatherReadings = document.querySelectorAll('.weather-reading');
    weatherReadings.forEach(reading => {
        reading.style.borderLeft = '4px solid #dc3545';
    });
    
    setTimeout(() => {
        weatherReadings.forEach(reading => {
            reading.style.borderLeft = '';
        });
    }, 3000);
}

function enableManualInput() {
    // Enable manual input for weather fields
    const weatherFields = ['id_temperature_high', 'id_temperature_low', 'id_humidity', 'id_wind_speed', 'id_weather_condition'];
    
    weatherFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.style.backgroundColor = '#fff3cd';
            field.placeholder = 'Enter manually';
        }
    });
}

function updateWeatherLoadingState(isLoading) {
    const periods = ['morning', 'afternoon'];
    
    periods.forEach(period => {
        const descElement = document.getElementById(`${period}WeatherDesc`);
        const iconElement = document.getElementById(`${period}WeatherIcon`);
        
        if (isLoading) {
            if (descElement) descElement.textContent = 'Fetching weather data...';
            if (iconElement) iconElement.innerHTML = '<i class="fas fa-spinner fa-spin text-secondary"></i>';
        }
    });
}

async function updateProjectLocation() {
    const projectSelect = document.getElementById('id_project');
    const locationInput = document.getElementById('siteLocation');
    
    if (!projectSelect || !locationInput || !projectSelect.value) {
        if (locationInput) locationInput.value = '';
        return;
    }
    
    try {
        const response = await fetch(`/diary/api/project-location/${projectSelect.value}/`);
        const data = await response.json();
        
        if (data.location) {
            locationInput.value = data.location;
            // Auto-fetch weather for new location
            setTimeout(() => fetchWeatherData(), 500);
        }
    } catch (error) {
        console.error('Error fetching project location:', error);
    }
}

function getLocationVariants(fullLocation) {
    const parts = fullLocation.split(',').map(part => part.trim());
    const variants = [];
    
    // Known Philippine cities
    const knownCities = ['manila', 'quezon city', 'makati', 'taguig', 'pasig', 'mandaluyong', 'san juan', 'marikina', 'pasay', 'paranaque', 'las pinas', 'muntinlupa', 'pateros', 'valenzuela', 'malabon', 'navotas', 'caloocan', 'cebu', 'davao', 'iloilo', 'bacolod', 'cagayan', 'zamboanga', 'baguio', 'tagaytay', 'naga'];
    
    // 1. Try original location first
    variants.push(fullLocation);
    
    // 2. Try with Philippines appended if not already there
    if (!fullLocation.toLowerCase().includes('philippines')) {
        variants.push(`${fullLocation}, Philippines`);
    }
    
    // 3. Find and try known cities
    let foundCity = null;
    for (const part of parts) {
        const cleanPart = part.toLowerCase().trim();
        for (const city of knownCities) {
            if (cleanPart === city || cleanPart.includes(city)) {
                foundCity = city.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                break;
            }
        }
        if (foundCity) break;
    }
    
    // 4. Try just the city if found
    if (foundCity) {
        variants.push(foundCity);
        variants.push(`${foundCity}, Philippines`);
    }
    
    // 5. Try the last part (usually the city/region)
    if (parts.length > 1) {
        const lastPart = parts[parts.length - 1];
        if (lastPart.toLowerCase() !== 'philippines') {
            variants.push(lastPart);
            variants.push(`${lastPart}, Philippines`);
        }
    }
    
    // 6. Fallback to Manila
    variants.push('Manila, Philippines');
    
    // Remove duplicates while preserving order
    return [...new Set(variants)];
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global access
window.fetchWeatherData = fetchWeatherData;
window.updateWeatherDisplay = updateWeatherDisplay;