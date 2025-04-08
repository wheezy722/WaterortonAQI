#!/usr/bin/env python3
import os
import requests
from datetime import datetime
import random
import tweepy

# --- Dynamic Tweet Pools ---
TEMPLATES = {
    "low": [
        # Location-Specific (7 Tweets)
        "The air in Water Orton is fresh and clean today. A great day for outdoor activities.",
        "Water Orton is enjoying excellent air quality today. Perfect for a morning jog or walk.",
        "Crisp air and clear skies in Water Orton make today ideal for outdoor plans.",
        "With pristine air in Water Orton, it’s a wonderful time to enjoy nature.",
        "Water Orton’s air is perfect today. Take a deep breath and enjoy the fresh conditions.",
        "Clear and clean air surrounds Water Orton today. A fantastic day to be outdoors.",
        "The air quality in Water Orton is as good as it gets. Time to make the most of it.",
        # General (13 Tweets)
        "Fresh air and sunshine make today perfect for outdoor fun.",
        "Excellent air conditions mean it’s a great time to connect with nature.",
        "The air feels crisp and clean today. Perfect for exploring the outdoors.",
        "Today’s air quality is fantastic. Time to step outside and enjoy!",
        "Clean air like this deserves appreciation—spend time outdoors.",
        "It’s a rare day of fresh, pristine air. A perfect excuse to go outside.",
        "Breathe deeply and enjoy today’s excellent air quality.",
        "With air this clean, it’s an ideal day for outdoor relaxation.",
        "Perfect air quality today—great for any outdoor adventure.",
        "Fresh, clean air means it’s a great time for outdoor activities.",
        "The outdoors is calling with air quality this refreshing.",
        "Today’s air feels invigorating—make the most of it outside.",
        "Such crisp air makes for a beautiful day to enjoy nature."
    ],
    "mediocre": [
        # Location-Specific (7 Tweets)
        "Water Orton’s air quality is moderate today. Sensitive individuals may want to stay indoors.",
        "Air quality in Water Orton is fair but manageable. Take precautions if spending time outdoors.",
        "Moderate pollution in Water Orton means shorter outdoor activities are ideal.",
        "Water Orton’s air is hovering in the moderate range today. Limit exposure if sensitive.",
        "Conditions in Water Orton are fair today—consider breaks indoors during outdoor plans.",
        "Today’s air quality in Water Orton isn’t perfect, but it’s manageable for most.",
        "If sensitive to pollution, take it slow in Water Orton today as conditions are mediocre.",
        # General (13 Tweets)
        "Moderate air quality today—light outdoor activities are fine, but pace yourself.",
        "Conditions are fair, but prolonged exposure outdoors may cause discomfort.",
        "Average pollution levels persist—sensitive groups should take it easy.",
        "Not the best air day, but manageable for most. Take breaks if necessary.",
        "Moderate air pollution calls for reduced exertion outdoors, especially for sensitive individuals.",
        "A fair air day means outdoor plans are fine but should be adjusted as needed.",
        "Air pollution is manageable today—pace yourself and stay hydrated.",
        "Outdoor activities are okay today, but sensitive groups should monitor exposure.",
        "Consider balancing outdoor and indoor activities during today’s moderate air quality.",
        "Mild pollution levels persist—take precautions if you feel irritation outdoors.",
        "Outdoor exposure is manageable, but frequent breaks indoors may help.",
        "Sensitive groups should consider alternative plans indoors to limit exposure.",
        "Moderate air conditions mean light outdoor activities are ideal."
    ],
    "high": [
        # Location-Specific (7 Tweets)
        "Air quality in Water Orton is poor today. Limit outdoor plans where possible.",
        "Pollution levels are elevated in Water Orton—take precautions and reduce exposure.",
        "Water Orton’s air today is unhealthy. Masks are recommended for outdoor activities.",
        "Poor air quality in Water Orton means sensitive groups should stay indoors.",
        "Pollution in Water Orton is concerning today—plan your day with safety in mind.",
        "Today’s air is unhealthy in Water Orton. Avoid exertion and limit exposure outside.",
        "If you’re sensitive to pollution, Water Orton’s air today requires extra precautions.",
        # General (13 Tweets)
        "Poor air quality persists—stay safe and minimize time outdoors.",
        "High pollution levels call for reduced outdoor exposure and frequent breaks indoors.",
        "Today’s air isn’t healthy—consider masks and air purifiers if necessary.",
        "Limit your time outdoors as poor air conditions persist.",
        "Sensitive individuals should avoid outdoor exposure entirely during today’s high pollution.",
        "Elevated pollution levels mean indoor activities are a safer option.",
        "Poor air quality could impact breathing comfort—take precautions as needed.",
        "Minimize outdoor exposure where possible to avoid irritation from pollution.",
        "With unhealthy air conditions today, prioritize safety indoors.",
        "Poor air quality means it’s best to avoid vigorous activities outdoors.",
        "Take care today—pollution levels may cause discomfort for some.",
        "Outdoor activities should be kept to a minimum during today’s poor air quality.",
        "Protect your health today—reduce outdoor exposure and consider indoor alternatives."
    ],
    "emergency": [
        # Location-Specific (7 Tweets)
        "Dangerous air pollution levels detected in Water Orton—avoid outdoor exposure entirely.",
        "Critical pollution persists in Water Orton today. Everyone is advised to stay indoors.",
        "Emergency alert for Water Orton—air quality is hazardous. Limit all exposure immediately.",
        "Severe air conditions in Water Orton pose significant health risks. Take care indoors.",
        "Water Orton’s air today is dangerously unhealthy—close all windows and prioritize safety.",
        "Extremely high pollution levels in Water Orton mean masks and air purifiers are essential.",
        "Hazardous air quality persists in Water Orton today. Remain vigilant and stay indoors.",
        # General (13 Tweets)
        "Critical air pollution levels require everyone to limit outdoor exposure entirely.",
        "Severe conditions mean everyone should remain indoors for safety.",
        "Avoid outdoor exertion—air quality poses serious health risks today.",
        "Emergency air pollution alert—stay indoors and minimize exposure completely.",
        "Hazardous air conditions call for vigilance—close windows and use air purifiers if possible.",
        "With air this unhealthy, outdoor exposure should be avoided entirely.",
        "Masks are mandatory today as air pollution reaches dangerous levels.",
        "Severe air pollution persists—monitor symptoms and prioritize health indoors.",
        "Everyone is advised to remain indoors and avoid exertion due to extreme pollution.",
        "Serious air quality concerns mean limiting all exposure and staying safe indoors.",
        "Emergency air conditions pose significant risks today—remain vigilant.",
        "Unhealthy air quality persists—close windows and doors to reduce exposure.",
        "Dangerous pollution levels require staying indoors and minimizing risks completely."
    ]
}

# --- Load Credentials ---
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
AIRLY_API_KEY = os.getenv('AIRLY_API_KEY')

# List of sensors with names (for fetching data and potential outlier highlighting)
SENSORS = [
    {"id": 118480, "name": "Birmingham Road (Shops)"},
    {"id": 118481, "name": "Station Road (East)"},
    {"id": 118482, "name": "Church Lane (South)"},
    {"id": 118483, "name": "Park Avenue (North)"},
    {"id": 118484, "name": "High Street (West)"}
]

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
        no2  = next((x["value"] for x in current_values if x["name"] == "NO2"), None)
        no   = next((x["value"] for x in current_values if x["name"] == "NO"), None)
        pollutants = {"PM2.5": pm25, "PM10": pm10, "NO2": no2, "NO": no}
        return {"sensor_name": sensor["name"], "pollutants": {k: v for k, v in pollutants.items() if v is not None}}
    except requests.RequestException as e:
        print(f"Error fetching data for sensor {sensor_id}: {e}")
        return None

def get_air_quality_for_all_sensors(sensors):
    """
    Fetches air quality data from all sensors and aggregates it.
    Returns a tuple: (aggregated average values, sensor result with highest reading).
    """
    all_results = []
    for sensor in sensors:
        result = get_air_quality(sensor)
        if result:
            all_results.append(result)
    if not all_results:
        return None

    aggregated = {}
    for result in all_results:
        for pollutant, value in result["pollutants"].items():
            aggregated.setdefault(pollutant, []).append(value)
    avg_data = {k: sum(v)/len(v) for k, v in aggregated.items()}

    # Identify the sensor with the highest reading (for any pollutant)
    def max_reading(result):
        return max(result["pollutants"].values()) if result["pollutants"] else 0
    max_data = max(all_results, key=max_reading)
    
    return avg_data, max_data

def determine_pollution_level(pollutants):
    """
    Determines pollution level based on DEFRA guidelines. Uses the worst reading among pollutants.
    DEFRA thresholds (values in µg/m³, with NO as a placeholder):
      PM2.5: moderate=12, high=24, emergency=36;
      PM10: moderate=17, high=34, emergency=50;
      NO2:  moderate=67, high=134, emergency=200;
      NO:   moderate=25, high=50, emergency=75.
    """
    DEFRA_LIMITS = {
        "PM2.5": {"moderate": 12, "high": 24, "emergency": 36},
        "PM10":  {"moderate": 17, "high": 34, "emergency": 50},
        "NO2":   {"moderate": 67, "high": 134, "emergency": 200},
        "NO":    {"moderate": 25, "high": 50, "emergency": 75}
    }
    level = "low"
    for pollutant, value in pollutants.items():
        limits = DEFRA_LIMITS.get(pollutant)
        if limits:
            if value > limits["emergency"]:
                return "emergency"
            elif value > limits["high"]:
                level = "high"
            elif value > limits["moderate"] and level not in ("high", "emergency"):
                level = "mediocre"
    return level

def prepare_tweet(sensors):
    """
    Prepares a tweet based on aggregated sensor data.
    Selects the pollution level based on average readings and checks for an outlier sensor.
    Then randomly selects one tweet from the corresponding pool. If an outlier exists,
    appends a note indicating which sensor shows higher pollution.
    """
    results = get_air_quality_for_all_sensors(sensors)
    if not results:
        return "Air quality data is unavailable at this time. Please check back later."
    
    avg_data, max_data = results
    level_avg = determine_pollution_level(avg_data)
    level_max = determine_pollution_level(max_data["pollutants"])
    
    # If there’s a discrepancy and the max reading is higher, we note it.
    overall_level = level_avg
    note = ""
    if level_max != level_avg:
        overall_level = level_max
        note = f" Note: {max_data['sensor_name']} reports higher pollution levels."
    
    tweet = random.choice(TEMPLATES[overall_level])
    return tweet + note

def post_tweet(text):
    """
    Posts the tweet using the Twitter API.
    """
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET_KEY,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
    )
    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data.get("id") if response.data else "unknown"
        print(f"Tweet posted successfully! Tweet ID: {tweet_id}")
    except Exception as e:
        print(f"Error posting tweet: {e}")

def main():
    """
    Checks if the current time is within a tweet window and, if so, prepares and posts a tweet.
    Tweet windows are defined as:
      - Morning: 08:00 - 10:30
      - Midday: 12:00 - 13:30
      - Afternoon: 16:00 - 17:30
    """
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    if (8 <= current_hour < 10) or (current_hour == 10 and current_minute <= 30):
        window = "morning"
    elif (12 <= current_hour < 13) or (current_hour == 13 and current_minute <= 30):
        window = "midday"
    elif (16 <= current_hour < 17) or (current_hour == 17 and current_minute <= 30):
        window = "afternoon"
    else:
        print("Not within tweet window. No tweet will be sent.")
        return
    
    tweet_text = prepare_tweet(SENSORS)
    print(f"Prepared tweet: {tweet_text}")
    post_tweet(tweet_text)

if __name__ == "__main__":
    main()
