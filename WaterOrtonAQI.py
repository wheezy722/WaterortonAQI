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

# --- Fact Pool (50 Facts) ---

FACTS = [
    # Pollutant Definitions (10 facts)
    "PM2.5 refers to tiny particles smaller than 2.5µm - small enough to penetrate deep into your lungs.",
    "PM10 particles are larger than PM2.5 but can still cause respiratory irritation and health issues.",
    "NO2 (Nitrogen Dioxide) is produced by vehicle exhaust and industrial emissions and can worsen asthma.",
    "Fine particulate matter like PM2.5 can enter your bloodstream and affect heart health.",
    "Ozone (O3) is a pollutant that can irritate your respiratory tract and is a major component of smog.",
    "High levels of PM10 can cause discomfort and respiratory issues, especially in vulnerable individuals.",
    "Exposure to NO2 can reduce lung function and increase susceptibility to respiratory infections.",
    "Air quality readings often emphasize PM2.5 due to its high potential for harm.",
    "Particulate matter pollution is linked to cardiovascular diseases and reduced life expectancy.",
    "PM2.5 is commonly generated by burning fossil fuels such as coal, oil, and wood.",
    # Thresholds and Standards (10 facts)
    "DEFRA thresholds for PM2.5 are: moderate >12 µg/m³, high >24 µg/m³, and emergency >36 µg/m³.",
    "WHO guidelines recommend stricter limits for PM2.5: an annual average <5 µg/m³ and a daily limit <15 µg/m³.",
    "DEFRA thresholds for PM10 are: moderate >17 µg/m³, high >34 µg/m³, and emergency >50 µg/m³.",
    "WHO suggests that PM10 should not exceed 45 µg/m³ daily to maintain safe air quality.",
    "DEFRA’s threshold for NO2 is: moderate >67 µg/m³, high >134 µg/m³, and emergency >200 µg/m³.",
    "DEFRA standards are tailored for UK conditions, reflecting local air quality challenges.",
    "WHO thresholds are based on comprehensive global research aimed at protecting public health.",
    "Emergency air pollution levels signal an immediate health risk requiring urgent action.",
    "DEFRA’s guidelines help translate pollutant levels into actionable public health advice.",
    "WHO’s stricter thresholds underline the importance of reducing long-term pollution exposure.",
    # Health Effects (10 facts)
    "Long-term exposure to PM2.5 can increase the risk of heart disease, stroke, and lung cancer.",
    "Poor air quality may aggravate asthma symptoms and cause respiratory irritation.",
    "High NO2 levels are linked to reduced lung function and a higher risk of bronchitis.",
    "Children are especially vulnerable to air pollution due to their developing lungs.",
    "Exposure to elevated pollutant levels during pregnancy can lead to complications like low birth weight.",
    "Air pollution has been associated with mental health issues such as anxiety and depression.",
    "Chronic exposure to pollutants worsens respiratory conditions like COPD.",
    "Long-term exposure to air pollution has been linked to reduced cognitive function in older adults.",
    "Poor air quality weakens respiratory defenses, increasing the risk of infections.",
    "High pollution days can trigger symptoms such as headaches, fatigue, and shortness of breath.",
    # Protection Tips (10 facts)
    "Reduce exposure by staying indoors on high pollution days and keeping windows closed.",
    "Using an air purifier with a HEPA filter can markedly improve indoor air quality.",
    "Wearing an N95 mask can help block dangerous particles like PM2.5 during outdoor exposure.",
    "Avoid vigorous outdoor exercise during peak pollution hours to protect your lungs.",
    "Indoor plants such as spider plants and aloe vera can naturally filter contaminants.",
    "Monitor air quality apps to plan your outings during periods of lower pollution.",
    "Ensure proper home ventilation during low pollution periods to clear indoor toxins.",
    "Staying well hydrated may help your body cope with the effects of pollutants.",
    "On high pollution days, opt for indoor activities—especially for children and the elderly.",
    "Avoid heavily trafficked areas to minimize exposure to vehicle emissions.",
    # Environmental Insights (10 facts)
    "Air pollution contributes to climate change by increasing greenhouse gas emissions.",
    "Smog is more prevalent in winter months due to higher fossil fuel consumption for heating.",
    "Urban greenery, such as trees and parks, naturally helps filter pollutants from the air.",
    "Industrial sources, including power plants, are major contributors to PM2.5 emissions.",
    "Vehicle emissions, particularly from diesel engines, are a leading source of NO2.",
    "Air quality can be significantly worse in valleys where pollutants may become trapped.",
    "Wildfires can cause dramatic spikes in particulate matter, affecting distant regions.",
    "Indoor pollution—from cooking, smoking, etc.—can be as harmful as outdoor air pollution.",
    "Rainfall can temporarily improve air quality by washing pollutants from the atmosphere.",
    "Transitioning to renewable energy sources, like wind and solar, helps reduce emissions."
]

# --- Twitter and Airly Credentials ---
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
AIRLY_API_KEY = os.getenv('AIRLY_API_KEY')

# --- Sensors List ---
SENSORS = [
    {"id": 118480, "name": "Birmingham Road "},
    {"id": 118482, "name": "Mytton Road"},
    {"id": 118495, "name": "Marsh Lane"},
    {"id": 118483, "name": "Plank Lane"},
    {"id": 118484, "name": "Watton Lane"}
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
    Aggregates air quality data from all sensors.
    Returns a tuple: (average pollutant readings, sensor data with the highest reading).
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
    def max_reading(result):
        return max(result["pollutants"].values()) if result["pollutants"] else 0
    max_data = max(all_results, key=max_reading)
    return avg_data, max_data

def determine_pollution_level(pollutants):
    """
    Determines the pollution level based on DEFRA thresholds.
    Returns "low", "mediocre", "high", or "emergency".
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

def prepare_sensor_tweet():
    """
    Prepares a tweet based on sensor data.
    Determines the overall pollution level and randomly selects a tweet
    from the corresponding pool. If an outlier sensor exists, a note is appended.
    """
    results = get_air_quality_for_all_sensors(SENSORS)
    if not results:
        return "Air quality data is unavailable at this time. Please check back later."
    avg_data, max_data = results
    level_avg = determine_pollution_level(avg_data)
    level_max = determine_pollution_level(max_data["pollutants"])
    overall_level = level_avg
    note = ""
    if level_max != level_avg:
        overall_level = level_max
        note = f" Note: {max_data['sensor_name']} reports higher pollution levels."
    tweet = random.choice(TEMPLATES[overall_level])
    return tweet + note

def prepare_fact_tweet():
    """
    Prepares an educational fact tweet by selecting a random fact from the FACTS pool.
    """
    fact = random.choice(FACTS)
    return fact

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

def sensor_tweet_job():
    tweet_text = prepare_sensor_tweet()
    print(f"Sensor Tweet: {tweet_text}")
    post_tweet(tweet_text)

def fact_tweet_job():
    tweet_text = prepare_fact_tweet()
    print(f"Fact Tweet: {tweet_text}")
    post_tweet(tweet_text)

def main():
    """
    Checks the current time and sends a tweet if within one of the designated windows:
      - Morning sensor tweet between 08:00 and 09:00
      - Midday sensor tweet between 12:00 and 13:00
      - Afternoon sensor tweet between 16:00 and 17:00
      - Fact tweet between 18:00 and 19:00
    If the current time is outside any window, nothing is sent.
    """
    now = datetime.now()
    current_hour = now.hour

    if 8 <= current_hour < 9:
        print("Within morning window. Sending sensor tweet.")
        sensor_tweet_job()
    elif 12 <= current_hour < 13:
        print("Within midday window. Sending sensor tweet.")
        sensor_tweet_job()
    elif 16 <= current_hour < 17:
        print("Within afternoon window. Sending sensor tweet.")
        sensor_tweet_job()
    elif 18 <= current_hour < 19:
        print("Within evening window. Sending fact tweet.")
        fact_tweet_job()
    else:
        print("Current time not in any tweet window. No tweet will be sent.")

if __name__ == "__main__":
    main()
