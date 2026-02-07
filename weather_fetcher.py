import requests

def get_weather(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,rain,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,rain_sum,wind_speed_10m_max",
        "past_days": 14,
        "forecast_days": 1,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return {"current": data["current"], "daily": data["daily"]}

if __name__ == "__main__":
    locations = {
        "Nairobi, Kenya": (-1.286, 36.817),
        "Mumbai, India": (19.076, 72.877),
        "Oxford, UK": (51.752, -1.258),
    }
    for name, (lat, lon) in locations.items():
        print(f"\n📍 {name}")
        weather = get_weather(lat, lon)
        c = weather["current"]
        d = weather["daily"]
        print(f"  🌡️ Temp: {c['temperature_2m']}°C")
        print(f"  🌧️ Rain: {c['rain']}mm")
        print(f"  💧 Humidity: {c['relative_humidity_2m']}%")
        print(f"  💨 Wind: {c['wind_speed_10m']} km/h")
        rain_history = [r or 0 for r in d['rain_sum']]
        print(f"  🌧️ Total rain 14 days: {sum(rain_history):.1f}mm")
