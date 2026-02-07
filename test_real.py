from weather_fetcher import get_weather
from disaster_detector import DisasterDetector

weather = get_weather(-1.286, 36.817)
detector = DisasterDetector()
detector.train(weather["daily"])
result = detector.detect(weather["current"], weather["daily"])

print(f"Nairobi right now: {result['type']}")
print(f"Rule says: {result['rule_detector']['result']}")
print(f"ML says: {result['ml_detector']['result']}")
print(f"Disaster? {result['disaster']}")
