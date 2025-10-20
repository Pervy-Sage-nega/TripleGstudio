// OpenWeatherMap API configuration
const OPENWEATHER_API_KEY = 'YOUR_API_KEY'; // Replace with your actual API key
const OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5';

class WeatherService {
    constructor() {
        this.location = null;
        this.weatherData = {
            morning: null,
            afternoon: null
        };
        
        this.init();
    }
    
    init() {
        // Initialize DOM elements
        this.detectLocationBtn = document.getElementById('detectLocation');
        this.refreshWeatherBtn = document.getElementById('refreshWeather');
        this.locationInput = document.getElementById('siteLocation');
        
        // Bind event listeners
        this.detectLocationBtn.addEventListener('click', () => this.detectLocation());
        this.refreshWeatherBtn.addEventListener('click', () => this.refreshWeather());
        this.locationInput.addEventListener('change', () => this.handleLocationInput());
        
        // Initial weather fetch
        this.detectLocation();
    }
    
    async detectLocation() {
        try {
            this.showLoading();
            
            if ('geolocation' in navigator) {
                const position = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(resolve, reject);
                });
                
                this.location = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                };
                
                // Get location name from coordinates
                await this.reverseGeocode();
                await this.fetchWeather();
            } else {
                throw new Error('Geolocation is not supported by your browser');
            }
        } catch (error) {
            this.showError('Could not detect location. Please enter it manually.');
            console.error('Location detection error:', error);
        }
    }
    
    async reverseGeocode() {
        try {
            const response = await fetch(
                `${OPENWEATHER_BASE_URL}/geo/1.0/reverse?lat=${this.location.lat}&lon=${this.location.lon}&limit=1&appid=${OPENWEATHER_API_KEY}`
            );
            const data = await response.json();
            
            if (data && data[0]) {
                const locationName = `${data[0].name}, ${data[0].country}`;
                this.locationInput.value = locationName;
            }
        } catch (error) {
            console.error('Reverse geocoding error:', error);
        }
    }
    
    async handleLocationInput() {
        try {
            const location = this.locationInput.value.trim();
            if (!location) return;
            
            this.showLoading();
            
            // Convert location name to coordinates
            const response = await fetch(
                `${OPENWEATHER_BASE_URL}/geo/1.0/direct?q=${encodeURIComponent(location)}&limit=1&appid=${OPENWEATHER_API_KEY}`
            );
            const data = await response.json();
            
            if (data && data[0]) {
                this.location = {
                    lat: data[0].lat,
                    lon: data[0].lon
                };
                await this.fetchWeather();
            } else {
                throw new Error('Location not found');
            }
        } catch (error) {
            this.showError('Could not find the specified location. Please try again.');
            console.error('Location search error:', error);
        }
    }
    
    async fetchWeather() {
        try {
            if (!this.location) throw new Error('No location set');
            
            this.showLoading();
            
            // Get 5-day forecast with 3-hour intervals
            const response = await fetch(
                `${OPENWEATHER_BASE_URL}/forecast?lat=${this.location.lat}&lon=${this.location.lon}&units=metric&appid=${OPENWEATHER_API_KEY}`
            );
            const data = await response.json();
            
            if (!data || !data.list) throw new Error('Invalid weather data');
            
            // Process forecast data for 8 AM and 2 PM readings
            const today = new Date();
            const todayStr = today.toISOString().split('T')[0];
            
            // Find 8 AM and 2 PM forecasts
            const morning = data.list.find(item => {
                const itemDate = new Date(item.dt * 1000);
                return itemDate.toISOString().split('T')[0] === todayStr && itemDate.getHours() === 8;
            });
            
            const afternoon = data.list.find(item => {
                const itemDate = new Date(item.dt * 1000);
                return itemDate.toISOString().split('T')[0] === todayStr && itemDate.getHours() === 14;
            });
            
            this.weatherData = {
                morning: this.processWeatherData(morning),
                afternoon: this.processWeatherData(afternoon)
            };
            
            this.updateUI();
        } catch (error) {
            this.showError('Could not fetch weather data. Please try again later.');
            console.error('Weather fetch error:', error);
        }
    }
    
    processWeatherData(data) {
        if (!data) return null;
        
        return {
            temp: Math.round(data.main.temp),
            humidity: data.main.humidity,
            windSpeed: Math.round(data.wind.speed * 3.6), // Convert m/s to km/h
            precipitation: data.rain ? data.rain['3h'] || 0 : 0,
            description: data.weather[0].description,
            icon: data.weather[0].icon
        };
    }
    
    updateUI() {
        // Update morning weather
        if (this.weatherData.morning) {
            document.getElementById('morningTemp').textContent = this.weatherData.morning.temp;
            document.getElementById('morningWind').textContent = this.weatherData.morning.windSpeed;
            document.getElementById('morningHumidity').textContent = this.weatherData.morning.humidity;
            document.getElementById('morningPrecipitation').textContent = this.weatherData.morning.precipitation;
            document.getElementById('morningWeatherDesc').textContent = this.capitalizeFirst(this.weatherData.morning.description);
            document.getElementById('morningWeatherIcon').innerHTML = 
                `<img src="https://openweathermap.org/img/wn/${this.weatherData.morning.icon}@2x.png" alt="Weather icon">`;
            
            // Store morning weather data
            document.getElementById('weatherMorning').value = JSON.stringify(this.weatherData.morning);
        }
        
        // Update afternoon weather
        if (this.weatherData.afternoon) {
            document.getElementById('afternoonTemp').textContent = this.weatherData.afternoon.temp;
            document.getElementById('afternoonWind').textContent = this.weatherData.afternoon.windSpeed;
            document.getElementById('afternoonHumidity').textContent = this.weatherData.afternoon.humidity;
            document.getElementById('afternoonPrecipitation').textContent = this.weatherData.afternoon.precipitation;
            document.getElementById('afternoonWeatherDesc').textContent = this.capitalizeFirst(this.weatherData.afternoon.description);
            document.getElementById('afternoonWeatherIcon').innerHTML = 
                `<img src="https://openweathermap.org/img/wn/${this.weatherData.afternoon.icon}@2x.png" alt="Weather icon">`;
            
            // Store afternoon weather data
            document.getElementById('weatherAfternoon').value = JSON.stringify(this.weatherData.afternoon);
        }
        
        // Hide loading indicators
        this.hideLoading();
    }
    
    showLoading() {
        document.getElementById('morningWeatherIcon').innerHTML = '<i class="fas fa-sync fa-spin"></i>';
        document.getElementById('afternoonWeatherIcon').innerHTML = '<i class="fas fa-sync fa-spin"></i>';
        document.getElementById('morningWeatherDesc').textContent = 'Loading...';
        document.getElementById('afternoonWeatherDesc').textContent = 'Loading...';
    }
    
    hideLoading() {
        // Loading indicators are replaced by actual weather data in updateUI
    }
    
    showError(message) {
        // Create or update notification
        let notification = document.querySelector('.notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'notification error';
            document.body.appendChild(notification);
        }
        
        notification.innerHTML = `
            <i class="fas fa-exclamation-circle notification-icon"></i>
            <div class="notification-message">${message}</div>
            <button class="notification-close">&times;</button>
        `;
        
        notification.classList.add('show');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, 5000);
        
        // Close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.classList.remove('show');
        });
    }
    
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    async refreshWeather() {
        if (this.location) {
            await this.fetchWeather();
        } else if (this.locationInput.value.trim()) {
            await this.handleLocationInput();
        } else {
            await this.detectLocation();
        }
    }
}

// Initialize weather service when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.weatherService = new WeatherService();
}); 