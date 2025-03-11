#!/usr/bin/env python3
import os
import requests
from datetime import datetime
import tweepy
import time  # You can keep time import but we will remove while loop

# --- Pre-Planned Tweet Templates ---
TEMPLATES = {
    "morning": {
        "low": "Good morning! The air quality is excellent today. Take a deep breath and enjoy the fresh air. Perfect day for outdoor activities.",
        "mediocre": "Good morning! Air quality is moderate today. It's still okay to be outdoors, but if you're sensitive to pollution, consider taking it easy.",
        "high": "Good morning! Air quality is poor today. If possible, reduce outdoor activities and keep windows closed. Take care of yourself."
    },
    "midday": {
        "low": "At midday, the air quality is fantastic! Breathe easy and enjoy the rest of your day. #AirQuality",
        "mediocre": "At midday, the air quality is moderate. It's manageable, but sensitive groups should take precautions. #AirQuality",
        "high": "At midday, the air quality is poor. Please consider minimizing outdoor activities for now. Take care. #AirQuality",
        "emergency": "🚨 At midday, air pollution is critically high! 🚨\nStay indoors, avoid outdoor exposure, and prioritize your health. This is a serious risk. #AirQualityAlert"
    },
    "afternoon": {
        "low": "This afternoon's air quality is still fresh and clean! A great time to get outside and enjoy the day.",
        "mediocre": "Air quality is moderate this afternoon. It's manageable, but sensitive groups should limit outdoor exposure.",
        "high": "Air quality is poor this afternoon. Try to minimize outdoor activities and protect yourself as best as you can."
    },
    "emergency": "🚨 ALERT: Air quality has reached dangerously high levels! 🚨\n"
                 "⚠️ Avoid going outside.\n⚠️ Close all windows and doors.\n⚠️ Use air purifiers if available.\n"
                 "⚠️ Watch for symptoms like headaches, dizziness, or difficulty breathing.\n\n"
                 "Stay indoors and protect yourself. This is a serious health risk — take care!"
}

# --- Load Credentials from Environment Variables ---
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
AIRLY_API_KEY = os.getenv('AIRLY_API_KEY')
SENSOR_ID = 118480  # Birmingham Road (Shops)

# --- Authenticate with Twitter API ---
client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET_KEY,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

def get_air_quality(sensor_id):
    """
    Fetches air quality data from the Airly API.
    """
    print("Fetching air quality data...")
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

        # Handle missing data gracefully
        pollutants = {"PM2.5": pm25, "PM10": pm10, "NO2": no2, "NO": no}
        pollutants = {k: v for k, v in pollutants.items() if v is not None}

        if not pollutants:
            print("No valid air quality data available.")
            return None

        print(f"Fetched pollutants data: {pollutants}")
        return pollutants
    except requests.RequestException as e:
        print(f"Error fetching air quality data: {e}")
        return None

def determine_pollution_level(pollutants):
    """
    Determines pollution level based on WHO guidelines.
    """
    WHO_LIMITS = {"PM2.5": 15, "PM10": 45, "NO2": 40, "NO": 25}

    if not pollutants:
        return "unknown"

    emergency = any(pollutants.get(key, 0) > WHO_LIMITS[key] * 2 for key in pollutants)
    high = any(pollutants.get(key, 0) > WHO_LIMITS[key] for key in pollutants)
    mediocre = any(pollutants.get(key, 0) > WHO_LIMITS[key] / 2 for key in pollutants)

    if emergency:
        return "emergency"
    elif high:
        return "high"
    elif mediocre:
        return "mediocre"
    else:
        return "low"

def prepare_tweet(sensor_id, time_of_day):
    """
    Prepares a tweet based on pollution levels and time of day.
    """
    pollutants = get_air_quality(sensor_id)
    if not pollutants:
        return "Air quality data is unavailable at this time. Please check back later! #AirQuality"

    level = determine_pollution_level(pollutants)
    print(f"Determined pollution level: {level}")
    
    tweet = TEMPLATES[time_of_day][level] if level != "emergency" else TEMPLATES["emergency"]
    print(f"Prepared tweet: {tweet}")
    return tweet

def post_tweet(text):
    """
    Posts a tweet using the Twitter API.
    """
    print(f"Attempting to post tweet: {text}")
    try:
        response = client.create_tweet(text=text)
        print(f"Tweet posted successfully! Tweet ID: {response.data['id']}")
    except Exception as e:
        print(f"Error posting tweet: {e}")

def main():
    """
    Runs the scheduler once based on the current time.
    """
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute

    # Debug print statements for time checking
    print(f"Current time: {current_hour}:{current_minute}")

    # Determine time of day and check if within tweet window (8-8:30am, 12-12:30pm, 4-4:30pm)
    if (current_hour == 8 and 0 <= current_minute <= 30) or \
       (current_hour == 12 and 0 <= current_minute <= 30) or \
       (current_hour == 16 and 0 <= current_minute <= 30):
        print("Time is within tweet window.")
        # Set the time of day for tweet
        if current_hour < 12:
            time_of_day = "morning"
        elif current_hour < 13:
            time_of_day = "midday"
        elif current_hour < 17:
            time_of_day = "afternoon"

        tweet_text = prepare_tweet(SENSOR_ID, time_of_day)
        post_tweet(tweet_text)
    else:
        print("Not within tweet window. No tweet will be sent.")

if __name__ == "__main__":
    main()



