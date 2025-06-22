# weather_utils.py
import requests
from typing import Dict, Any, Optional
from app.config import settings
from app.models.advisory import WeatherAdvice
import logging

logger = logging.getLogger(__name__)

async def get_weather_data(region: str) -> Optional[Dict[str, Any]]:
    """Get weather data from API or return dummy data"""
    if not settings.WEATHER_API_KEY:
        # Return dummy weather data
        return {
            "temperature": 25.5,
            "humidity": 65,
            "weather_condition": "partly_cloudy",
            "region": region
        }
    
    try:
        url = f"{settings.WEATHER_API_URL}"
        params = {
            "q": region,
            "appid": settings.WEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather_condition": data["weather"][0]["main"].lower(),
            "region": region
        }
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return None

def generate_weather_advice(weather_data: Dict[str, Any]) -> WeatherAdvice:
    """Generate weather-based agricultural advice"""
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]
    condition = weather_data["weather_condition"]
    
    # Generate advice based on weather conditions
    if temp > 30:
        planting_advice = "High temperature detected. Consider planting heat-resistant varieties."
        irrigation_advice = "Increase watering frequency due to high temperature."
    elif temp < 15:
        planting_advice = "Low temperature. Consider using greenhouse or wait for warmer weather."
        irrigation_advice = "Reduce watering as evaporation is low in cool weather."
    else:
        planting_advice = "Good temperature for most crops. Proceed with normal planting."
        irrigation_advice = "Maintain regular watering schedule."
    
    if humidity > 80:
        pest_risk = "High humidity increases fungal disease risk. Monitor crops closely."
    elif humidity < 40:
        pest_risk = "Low humidity may stress plants. Ensure adequate irrigation."
    else:
        pest_risk = "Humidity levels are good for crop growth."
    
    return WeatherAdvice(
        temperature=temp,
        humidity=humidity,
        weather_condition=condition,
        planting_advice=planting_advice,
        irrigation_advice=irrigation_advice,
        pest_risk=pest_risk
    )