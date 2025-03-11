#!/usr/bin/env python3
import os
import requests
from datetime import datetime, timezone, timedelta
import tweepy
import schedule
import time

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
# --- Twitter API Credentials ---
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

AIRLY_API_KEY = os.getenv('AIRLY_API_KEY')
SENSOR_ID = 118480

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
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        current_values = data.get("current", {}).get("values", [])
        pm25 = next((x["value"] for x in current_values if x["name"] == "PM2.5"), None)
        pm10 = next((x["value"] for x in current_values if x["name"] == "PM10"), None)

        if pm25 is None and pm10 is not None:
            print("PM2.5 unavailable; using PM10 as fallback.")
            pm25 = pm10
        elif pm25 is None and pm10 is None:
            print("No air quality data available.")
            return None, None

        return pm25, pm10
    except requests.RequestException as e:
        print(f"Error fetching air quality data: {e}")
        return None, None

def determine_pollution_level(pm25, pm10):
    """
    Determines pollution level based on WHO guidelines.
    """
    WHO_LIMITS = {"PM2.5": 15, "PM10": 45}
    if pm25 > WHO_LIMITS["PM2.5"] * 2 or pm10 > WHO_LIMITS["PM10"] * 2:
        return "emergency"
    elif pm25 > WHO_LIMITS["PM2.5"] or pm10 > WHO_LIMITS["PM10"]:
        return "high"
    elif pm25 > WHO_LIMITS["PM2.5"] / 2 or pm10 > WHO_LIMITS["PM10"] / 2:
        return "mediocre"
    else:
        return "low"

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

def prepare_tweet(sensor_id, time_of_day):
    """
    Prepares a tweet based on pollution levels and time of day.
    """
    pm25, pm10 = get_air_quality(sensor_id)
    if pm25 is None or pm10 is None:
        return "Air quality data is unavailable at this time. Please check back later! #AirQuality"

    level = determine_pollution_level(pm25, pm10)
    return TEMPLATES[time_of_day][level] if level != "emergency" else TEMPLATES["emergency"]

def check_for_emergency(sensor_id):
    """
    Checks air quality every 30 minutes and tweets if pollution levels are dangerously high.
    """
    print("Checking for emergency pollution levels...")
    pm25, pm10 = get_air_quality(sensor_id)
    if pm25 is None or pm10 is None:
        print("No air quality data available for emergency check.")
        return

    level = determine_pollution_level(pm25, pm10)
    if level == "emergency":
        print("Emergency detected! Posting emergency tweet.")
        post_tweet(TEMPLATES["emergency"])

def should_send_scheduled_tweet():
    """
    Determines whether it is one of the scheduled times to send a standard tweet.
    Returns True if it is 8:00 AM, 12:00 PM, or 4:00 PM.
    """
    current_time = datetime.now().strftime("%H:%M")
    scheduled_times = ["08:00", "12:00", "16:00"]
    return current_time in scheduled_times

def main():
    # Check if it's a scheduled time to send a tweet
    if should_send_scheduled_tweet():
        print("It's a scheduled time. Sending a standard tweet...")
        time_of_day = "morning" if datetime.now().hour == 8 else "midday" if datetime.now().hour == 12 else "afternoon"
        scheduled_tweet = prepare_tweet(SENSOR_ID, time_of_day)
        if scheduled_tweet:
            post_tweet(scheduled_tweet)
    else:
        print("Not a scheduled time. Checking for emergencies only.")

    # Schedule emergency checks every 30 minutes
    schedule.every(30).minutes.do(check_for_emergency, SENSOR_ID)

    print("Starting scheduler...")
    while True:
        try:
            print("Scheduler is running... Waiting for the next task.")  # Heartbeat log
            schedule.run_pending()
            time.sleep(60)  # Wait for 60 seconds before checking again
        except Exception as e:
            print(f"Error in the main loop: {e}")

if __name__ == "__main__":
    main()
