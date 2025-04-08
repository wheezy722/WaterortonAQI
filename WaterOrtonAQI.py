#!/usr/bin/env python3
import os
import requests
from datetime import datetime
import tweepy

# --- Pre-Planned Tweet Templates ---
TEMPLATES = {
    "morning": {
        "low": "Good morning! The air quality is excellent today. Take a deep breath and enjoy the fresh air. Perfect day for outdoor activities.",
        "mediocre": "Good morning! Air quality is moderate today. It's still okay to be outdoors, but if you're sensitive to pollution, consider taking it easy.",
        "high": "Good morning! Air quality is poor today. If possible, reduce outdoor activities and keep windows closed. Take care of yourself."
    },
    "midday": {
        "low": "At midday, the air quality is fantastic. Breathe easy and enjoy the rest of your day.",
        "mediocre": "At midday, the air quality is moderate. It's manageable, but sensitive groups should take precautions.",
        "high": "At midday, the air quality is poor. Please consider minimizing outdoor activities for now. Take care.",
        "emergency": "ALERT: At midday, air pollution is critically high. Stay indoors, avoid outdoor exposure, and prioritize your health. This is a serious risk."
    },
    "afternoon": {
        "low": "This afternoon's air quality is still fresh and clean. A great time to get outside and enjoy the day.",
        "mediocre": "Air quality is moderate this afternoon. It's manageable, but sensitive groups should limit outdoor exposure.",
        "high": "Air quality is poor this afternoon. Try to minimize outdoor activities and protect yourself as best as you can."
    },
    "emergency": "ALERT: Air quality has reached dangerously high levels! Avoid going outside, close all windows and doors, and stay safe."
}

# --- Load Credentials from Environment Variables ---
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
AIRLY_API_KEY = os.getenv('AIRLY_API_KEY')

# List of sensor IDs and names
SENSORS = [
    {"id": 118480, "name": "Birmingham Road "},
    {"id": 118482, "name": "Mytton Road"},
    {"id": 118495, "name": "Marsh Lane (Shops)"},
    {"id": 118483, "name": "Plank Lane"},
    {"id": 118484, "name": "Watton Lane"}
]

# --- Authenticate with Twitter API ---
client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET_KEY,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

def get_air_quality(sensor):
    """
    Fetches air quality data from the Airly API for a single sensor.
    """
    sensor_id = sensor["id"]
    url = f"https://airapi.airly.eu/v2/measurements/installation?installationId={sensor_id}"
    headers = {"apikey": AIRLY_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        current_values = data.get("current", {}).get("values", [])
        pm25 = next((x["value"] for x in current_values if x["name"] == "PM2.5"), None)
        pm10 = next((x["value"] for x in current_values if x["name"] == "PM10"), None)
        no2 = next((x["value"] for x in current_values if x["name"] == "NO2"), None)
        no = next((x["value"] for x in current_values if x["name"] == "NO"), None)

        pollutants = {"PM2.5": pm25, "PM10": pm10, "NO2": no2, "NO": no}
        return {"sensor_name": sensor["name"], "pollutants": {k: v for k, v in pollutants.items() if v is not None}}
    except requests.RequestException as e:
        print(f"Error fetching data for sensor {sensor_id}: {e}")
        return None

def get_air_quality_for_all_sensors(sensors):
    """
    Fetches air quality data from all sensors and aggregates it.
    """
    all_pollutants = []
    for sensor in sensors:
        result = get_air_quality(sensor)
        if result:
            all_pollutants.append(result)

    if not all_pollutants:
        return None

    aggregated_data = {}
    for result in all_pollutants:
        for key, value in result["pollutants"].items():
            aggregated_data[key] = aggregated_data.get(key, []) + [value]

    avg_data = {key: sum(values) / len(values) for key, values in aggregated_data.items()}
    max_data = max(all_pollutants, key=lambda x: max(x["pollutants"].values()))
    return avg_data, max_data

def determine_pollution_level(pollutants):
    """
    Determines pollution level based on DEFRA guidelines.
    """
    DEFRA_LIMITS = {
        "PM2.5": {"moderate": 12, "high": 24, "emergency": 36},
        "PM10": {"moderate": 17, "high": 34, "emergency": 50},
        "NO2": {"moderate": 67, "high": 134, "emergency": 200},
        "NO": {"moderate": 25, "high": 50, "emergency": 75}  # Placeholder if needed
    }

    if any(pollutants.get(key, 0) > DEFRA_LIMITS[key]["emergency"] for key in pollutants):
        return "emergency"
    elif any(pollutants.get(key, 0) > DEFRA_LIMITS[key]["high"] for key in pollutants):
        return "high"
    elif any(pollutants.get(key, 0) > DEFRA_LIMITS[key]["moderate"] for key in pollutants):
        return "mediocre"
    else:
        return "low"

def prepare_tweet(sensors, time_of_day):
    """
    Prepares a tweet based on aggregated air quality data.
    """
    results = get_air_quality_for_all_sensors(sensors)
    if not results:
        return "Air quality data is unavailable at this time. Please check back later."

    avg_data, max_data = results
    avg_level = determine_pollution_level(avg_data)
    max_level = determine_pollution_level(max_data["pollutants"])

    if max_level == "emergency":
        tweet = TEMPLATES["emergency"]
    else:
        tweet = TEMPLATES[time_of_day][avg_level]
        if avg_level != max_level:
            tweet += f" Note: {max_data['sensor_name']} reports higher pollution levels reaching '{max_level}'."

    return tweet

def post_tweet(text):
    """
    Posts a tweet using the Twitter API.
    """
    try:
        response = client.create_tweet(text=text)
        print(f"Tweet posted successfully! Tweet ID: {response.data['id']}")
    except Exception as e:
        print(f"Error posting tweet: {e}")

def main():
    """
    Determines the time of day and posts the appropriate air quality tweet.
    """
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute

    if (8 <= current_hour < 10) or (current_hour == 10 and current_minute <= 30):
        time_of_day = "morning"
    elif (12 <= current_hour < 13) or (current_hour == 13 and current_minute <= 30):
        time_of_day = "midday"
    elif (16 <= current_hour < 17) or (current_hour == 17 and current_minute <= 30):
        time_of_day = "afternoon"
    else:
        print("Not within tweet window. No tweet will be sent.")
        return

    tweet_text = prepare_tweet(SENSORS, time_of_day)
    post_tweet(tweet_text)

if __name__ == "__main__":
    main()
