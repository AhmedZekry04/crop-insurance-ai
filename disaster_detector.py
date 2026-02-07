import numpy as np
from sklearn.ensemble import IsolationForest

class DisasterDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=100,
            random_state=42,
        )
        self.is_trained = False

    def train(self, daily_data: dict):
        temps_max = daily_data.get("temperature_2m_max", [])
        temps_min = daily_data.get("temperature_2m_min", [])
        rain = daily_data.get("rain_sum", [])
        wind = daily_data.get("wind_speed_10m_max", [])

        n = min(len(temps_max), len(temps_min), len(rain), len(wind))
        if n < 7:
            print("Not enough data to train")
            return

        features = []
        for i in range(n):
            features.append([
                temps_max[i] or 0,
                temps_min[i] or 0,
                rain[i] or 0,
                wind[i] or 0,
            ])

        self.model.fit(np.array(features))
        self.is_trained = True
        print(f"Model trained on {n} days of data")

    def detect(self, current: dict, daily_data: dict) -> dict:
        temp = current.get("temperature_2m", 20)
        rain = current.get("rain", 0)
        humidity = current.get("relative_humidity_2m", 50)
        wind = current.get("wind_speed_10m", 0)

        # DETECTOR A: Simple rules
        rain_history = [r or 0 for r in daily_data.get("rain_sum", [])]
        recent_rain = rain_history[-10:] if len(rain_history) >= 10 else rain_history

        rule_result = "NORMAL"
        rule_reason = ""

        if len(recent_rain) >= 7 and sum(recent_rain) < 2.0:
            rule_result = "DROUGHT"
            rule_reason = f"Only {sum(recent_rain):.1f}mm rain in {len(recent_rain)} days"
        elif rain > 50:
            rule_result = "FLOOD"
            rule_reason = f"Extreme rainfall: {rain}mm"
        elif temp < 2:
            rule_result = "FROST"
            rule_reason = f"Temperature: {temp}°C"
        elif temp > 45:
            rule_result = "HEAT_WAVE"
            rule_reason = f"Temperature: {temp}°C"

        # DETECTOR B: Isolation Forest
        ml_result = "NORMAL"
        ml_score = 0.0

        if self.is_trained:
            today_features = [[temp, temp - 5, rain, wind]]
            ml_score = float(self.model.score_samples(today_features)[0])
            if self.model.predict(today_features)[0] == -1:
                ml_result = "ANOMALY"

        # ENSEMBLE: both must agree
        is_disaster = (rule_result != "NORMAL") and (ml_result == "ANOMALY")

        return {
            "disaster": is_disaster,
            "type": rule_result if is_disaster else "NORMAL",
            "confidence": min(abs(ml_score), 1.0) if is_disaster else 0.0,
            "rule_detector": {"result": rule_result, "reason": rule_reason},
            "ml_detector": {"result": ml_result, "score": ml_score},
            "weather": {"temperature": temp, "rain": rain, "humidity": humidity, "wind": wind},
        }

if __name__ == "__main__":
    detector = DisasterDetector()

    normal_daily = {
        "temperature_2m_max": [25,26,24,27,25,26,25,24,26,27,25,26,24,25],
        "temperature_2m_min": [14,15,13,14,14,15,14,13,15,14,14,15,13,14],
        "rain_sum":           [2,5,0,3,1,4,2,0,3,5,2,1,3,2],
        "wind_speed_10m_max": [15,12,18,14,16,13,15,17,14,12,16,14,15,13],
    }
    detector.train(normal_daily)

    print("\n--- Test 1: Normal day ---")
    r = detector.detect({"temperature_2m":25,"rain":3,"relative_humidity_2m":65,"wind_speed_10m":14}, normal_daily)
    print(f"Result: {r['type']} | Disaster: {r['disaster']}")

    print("\n--- Test 2: Flood ---")
    r = detector.detect({"temperature_2m":20,"rain":80,"relative_humidity_2m":95,"wind_speed_10m":40}, normal_daily)
    print(f"Result: {r['type']} | Rule: {r['rule_detector']['result']} | ML: {r['ml_detector']['result']} | Disaster: {r['disaster']}")

    print("\n--- Test 3: Frost ---")
    r = detector.detect({"temperature_2m":-2,"rain":0,"relative_humidity_2m":80,"wind_speed_10m":5}, normal_daily)
    print(f"Result: {r['type']} | Rule: {r['rule_detector']['result']} | ML: {r['ml_detector']['result']} | Disaster: {r['disaster']}")

    print("\nAll tests done!")