#!/usr/bin/env python3
import os
import requests
from datetime import datetime
import random
import tweepy
import logging

# --- Dynamic Tweet Pools ---

def get_time_of_day():
    """Returns 'this morning', 'this lunchtime', or 'this evening' based on current time."""
    hour = datetime.now().hour
    if 7 <= hour < 12:
        return "this morning"
    elif 12 <= hour < 15:
        return "this lunchtime"
    elif 15 <= hour < 20:
        return "this evening"
    else:
        return "this evening"

TEMPLATES = {
    "low": [
        "🍃 Low pollution: The air in Water Orton is fresh and clean {time_of_day}. A great day for outdoor activities.",
        "🍃 Low pollution: Water Orton is enjoying excellent air quality {time_of_day}. Perfect for a morning jog or walk.",
        "🍃 Low pollution: Crisp air and clear skies in Water Orton make {time_of_day} ideal for outdoor plans.",
        "🍃 Low pollution: With pristine air in Water Orton {time_of_day}, it's a wonderful time to enjoy nature.",
        "🍃 Low pollution: Water Orton's air is perfect {time_of_day}. Take a deep breath and enjoy the fresh conditions.",
        "🍃 Low pollution: Clear and clean air surrounds Water Orton {time_of_day}. A fantastic day to be outdoors.",
        "🍃 Low pollution: The air quality in Water Orton is as good as it gets {time_of_day}. Time to make the most of it.",
        "🍃 Low pollution: Fresh air and sunshine make {time_of_day} perfect for outdoor fun.",
        "🍃 Low pollution: Excellent air conditions {time_of_day} mean it's a great time to connect with nature.",
        "🍃 Low pollution: The air feels crisp and clean {time_of_day}. Perfect for exploring the outdoors.",
        "🍃 Low pollution: {time_of_day}'s air quality is fantastic. Time to step outside and enjoy!",
        "🍃 Low pollution: Clean air like this {time_of_day} deserves appreciation—spend time outdoors.",
        "🍃 Low pollution: It's a rare {time_of_day} of fresh, pristine air. A perfect excuse to go outside.",
        "🍃 Low pollution: Breathe deeply and enjoy {time_of_day}'s excellent air quality.",
        "🍃 Low pollution: With air this clean {time_of_day}, it's an ideal day for outdoor relaxation.",
        "🍃 Low pollution: Perfect air quality {time_of_day}—great for any outdoor adventure.",
        "🍃 Low pollution: Fresh, clean air {time_of_day} means it's a great time for outdoor activities.",
        "🍃 Low pollution: The outdoors is calling with air quality this refreshing {time_of_day}.",
        "🍃 Low pollution: {time_of_day}'s air feels invigorating—make the most of it outside.",
        "🍃 Low pollution: Such crisp air {time_of_day} makes for a beautiful day to enjoy nature. "
    ],
    "mediocre": [
        "⚠️ Moderate pollution: Water Orton's air quality is moderate {time_of_day}. Sensitive individuals may want to stay indoors.",
        "⚠️ Moderate pollution: Air quality in Water Orton is fair but manageable {time_of_day}. Take precautions if spending time outdoors.",
        "⚠️ Moderate pollution: Moderate pollution in Water Orton means {time_of_day} is better for shorter outdoor activities.",
        "⚠️ Moderate pollution: Water Orton's air is hovering in the moderate range {time_of_day}. Limit exposure if sensitive.",
        "⚠️ Moderate pollution: Conditions in Water Orton are fair {time_of_day}—consider breaks indoors during outdoor plans.",
        "⚠️ Moderate pollution: {time_of_day}'s air quality in Water Orton isn't perfect, but it's manageable for most.",
        "⚠️ Moderate pollution: If sensitive to pollution, take it slow in Water Orton {time_of_day} as conditions are mediocre.",
        "⚠️ Moderate pollution: Moderate air quality {time_of_day}—light outdoor activities are fine, but pace yourself.",
        "⚠️ Moderate pollution: Conditions are fair {time_of_day}, but prolonged exposure outdoors may cause discomfort.",
        "⚠️ Moderate pollution: Average pollution levels persist {time_of_day}—sensitive groups should take it easy.",
        "⚠️ Moderate pollution: Not the best air {time_of_day}, but manageable for most. Take breaks if necessary.",
        "⚠️ Moderate pollution: Moderate air pollution {time_of_day} calls for reduced exertion outdoors, especially for sensitive individuals.",
        "⚠️ Moderate pollution: A fair air day means {time_of_day}'s outdoor plans are fine but should be adjusted as needed.",
        "⚠️ Moderate pollution: Air pollution is manageable {time_of_day}—pace yourself and stay hydrated.",
        "⚠️ Moderate pollution: Outdoor activities are okay {time_of_day}, but sensitive groups should monitor exposure.",
        "⚠️ Moderate pollution: Consider balancing outdoor and indoor activities during {time_of_day}'s moderate air quality.",
        "⚠️ Moderate pollution: Mild pollution levels persist {time_of_day}—take precautions if you feel irritation outdoors.",
        "⚠️ Moderate pollution: Outdoor exposure {time_of_day} is manageable, but frequent breaks indoors may help.",
        "⚠️ Moderate pollution: Sensitive groups should consider alternative plans indoors {time_of_day} to limit exposure.",
        "⚠️ Moderate pollution: Moderate air conditions {time_of_day} mean light outdoor activities are ideal."
    ],
    "high": [
        "🚨 High pollution: Air quality in Water Orton is poor {time_of_day}. Limit outdoor plans where possible.",
        "🚨 High pollution: Pollution levels are elevated in Water Orton {time_of_day}—take precautions and reduce exposure.",
        "🚨 High pollution: Water Orton's air {time_of_day} is unhealthy. Masks are recommended for outdoor activities.",
        "🚨 High pollution: Poor air quality in Water Orton {time_of_day} means sensitive groups should stay indoors.",
        "🚨 High pollution: Pollution in Water Orton is concerning {time_of_day}—plan your day with safety in mind.",
        "🚨 High pollution: {time_of_day}'s air is unhealthy in Water Orton. Avoid exertion and limit exposure outside.",
        "🚨 High pollution: If you're sensitive to pollution, Water Orton's air {time_of_day} requires extra precautions.",
        "🚨 High pollution: Poor air quality persists {time_of_day}—stay safe and minimize time outdoors.",
        "🚨 High pollution: High pollution levels {time_of_day} call for reduced outdoor exposure and frequent breaks indoors.",
        "🚨 High pollution: {time_of_day}'s air isn't healthy—consider masks and air purifiers if necessary.",
        "🚨 High pollution: Limit your time outdoors {time_of_day} as poor air conditions persist.",
        "🚨 High pollution: Sensitive individuals should avoid outdoor exposure entirely {time_of_day} during high pollution.",
        "🚨 High pollution: Elevated pollution levels {time_of_day} mean indoor activities are a safer option.",
        "🚨 High pollution: Poor air quality {time_of_day} could impact breathing comfort—take precautions as needed.",
        "🚨 High pollution: Minimize outdoor exposure {time_of_day} where possible to avoid irritation from pollution.",
        "🚨 High pollution: With unhealthy air conditions {time_of_day}, prioritize safety indoors.",
        "🚨 High pollution: Poor air quality {time_of_day} means it's best to avoid vigorous activities outdoors.",
        "🚨 High pollution: Take care {time_of_day}—pollution levels may cause discomfort for some.",
        "🚨 High pollution: Outdoor activities should be kept to a minimum {time_of_day} during poor air quality.",
        "🚨 High pollution: Protect your health {time_of_day}—reduce outdoor exposure and consider indoor alternatives."
    ],
    "emergency": [
        "🚨 Dangerous air pollution levels detected in Water Orton {time_of_day}—avoid outdoor exposure entirely.🚨",
        "🚨 Critical pollution persists in Water Orton {time_of_day}. Everyone is advised to stay indoors.🚨",
        "🚨 Emergency alert for Water Orton—air quality is hazardous {time_of_day}. Limit all exposure immediately.🚨",
        "🚨 Severe air conditions in Water Orton {time_of_day} pose significant health risks. Take care indoors.🚨",
        "🚨 Water Orton's air {time_of_day} is dangerously unhealthy—close all windows and prioritize safety.🚨",
        "🚨 Extremely high pollution levels in Water Orton {time_of_day} mean masks and air purifiers are essential.🚨",
        "🚨 Hazardous air quality persists in Water Orton {time_of_day}. Remain vigilant and stay indoors.🚨",
        "🚨 Critical air pollution levels {time_of_day} require everyone to limit outdoor exposure entirely.🚨",
        "🚨 Severe conditions {time_of_day} mean everyone should remain indoors for safety.🚨",
        "🚨 Avoid outdoor exertion {time_of_day}—air quality poses serious health risks today.🚨",
        "🚨 Emergency air pollution alert—stay indoors {time_of_day} and minimize exposure completely.🚨",
        "🚨 Hazardous air conditions {time_of_day} call for vigilance—close windows and use air purifiers if possible.🚨",
        "🚨 With air this unhealthy {time_of_day}, outdoor exposure should be avoided entirely.🚨",
        "🚨 Masks are mandatory {time_of_day} as air pollution reaches dangerous levels.🚨",
        "🚨 Severe air pollution persists {time_of_day}—monitor symptoms and prioritize health indoors.🚨",
        "🚨 Everyone is advised to remain indoors {time_of_day} and avoid exertion due to extreme pollution.🚨",
        "🚨 Serious air quality concerns {time_of_day} mean limiting all exposure and staying safe indoors.🚨",
        "🚨 Emergency air conditions {time_of_day} pose significant risks—remain vigilant.🚨",
        "🚨 Unhealthy air quality persists {time_of_day}—close windows and doors to reduce exposure.🚨",
        "🚨 Dangerous pollution levels {time_of_day} require staying indoors and minimizing risks completely.🚨"
    ]
}

# --- Fact Pool (50 Facts) ---

FACTS = [
    # Pollutant Definitions (10 facts)
    "Pollutant Definition: - PM2.5 refers to tiny particles smaller than 2.5µm - small enough to penetrate deep into your lungs.",
    "Pollutant Definition: - PM10 particles are larger than PM2.5 but can still cause respiratory irritation and health issues.",
    "Pollutant Information: - NO2 (Nitrogen Dioxide) is produced by vehicle exhaust and industrial emissions and can worsen asthma.",
    "Pollutant Information: - Fine particulate matter like PM2.5 can enter your bloodstream and affect heart health.",
    "Pollutant information: - Ozone (O3) is a pollutant that can irritate your respiratory tract and is a major component of smog.",
    "Pollutant Information: - High levels of PM10 can cause discomfort and respiratory issues, especially in vulnerable individuals.",
    "Pollutant Information: - Exposure to NO2 can reduce lung function and increase susceptibility to respiratory infections.",
    "Pollutant Information: - Air quality readings often emphasize PM2.5 due to its high potential for harm.",
    "Pollutant Information: - Particulate matter pollution is linked to cardiovascular diseases and reduced life expectancy.",
    "Pollutant Information: - PM2.5 is commonly generated by burning fossil fuels such as coal, oil, and wood.",
    # Thresholds and Standards (10 facts)
    "Pollutant Thresholds: - DEFRA thresholds for PM2.5 are: moderate >12 µg/m³, high >24 µg/m³, and emergency >36 µg/m³.",
    "Pollutant Thresholds: - WHO guidelines recommend stricter limits for PM2.5: an annual average <5 µg/m³ and a daily limit <15 µg/m³.",
    "Pollutant Thresholds: - DEFRA thresholds for PM10 are: moderate >17 µg/m³, high >34 µg/m³, and emergency >50 µg/m³.",
    "Pollutant Thresholds: - WHO suggests that PM10 should not exceed 45 µg/m³ daily to maintain safe air quality.",
    "Pollutant Thresholds: - DEFRA's threshold for NO2 is: moderate >67 µg/m³, high >134 µg/m³, and emergency >200 µg/m³.",
    "Pollutant Thresholds: - DEFRA standards are tailored for UK conditions, reflecting local air quality challenges.",
    "Pollutant Thresholds: - WHO thresholds are based on comprehensive global research aimed at protecting public health.",
    "Be Aware : Emergency air pollution levels signal an immediate health risk requiring urgent action.",
    "To Note: - DEFRA's guidelines help translate pollutant levels into actionable public health advice.",
    "To Note: - DEFRA and WHO have different guidelines. WHO's stricter thresholds underline the importance of reducing long-term pollution exposure.",
    # Health Effects (10 facts)
    "Health Effects: - Long-term exposure to PM2.5 can increase the risk of heart disease, stroke, and lung cancer.",
    "Health Effects: - Poor air quality may aggravate asthma symptoms and cause respiratory irritation.",
    "Health Effects: - High NO2 levels are linked to reduced lung function and a higher risk of bronchitis.",
    "Health Effects: - Children are especially vulnerable to air pollution due to their developing lungs.",
    "Health Effects: - Exposure to elevated pollutant levels during pregnancy can lead to complications like low birth weight.",
    "Health Effects: - Air pollution has been associated with mental health issues such as anxiety and depression.",
    "Health Effects: - Chronic exposure to pollutants worsens respiratory conditions like COPD.",
    "Health Effects: - Long-term exposure to air pollution has been linked to reduced cognitive function in older adults.",
    "Health Effects: - Poor air quality weakens respiratory defenses, increasing the risk of infections.",
    "Health Effects: - High pollution days can trigger symptoms such as headaches, fatigue, and shortness of breath.",
    # Protection Tips (10 facts)
    "Tips: - Reduce exposure by staying indoors on high pollution days and keeping windows closed.",
    "Tips: - Using an air purifier with a HEPA filter can markedly improve indoor air quality.",
    "Tips: - Wearing an N95 mask can help block dangerous particles like PM2.5 during outdoor exposure.",
    "Tips: - Avoid vigorous outdoor exercise during peak pollution hours to protect your lungs.",
    "Tips: - Indoor plants such as spider plants and aloe vera can naturally filter contaminants.",
    "Tips: - Monitor air quality apps to plan your outings during periods of lower pollution.",
    "Tips: - Ensure proper home ventilation during low pollution periods to clear indoor toxins.",
    "Tips: - Staying well hydrated may help your body cope with the effects of pollutants.",
    "Tips: - On high pollution days, opt for indoor activities—especially for children and the elderly.",
    "Tips: - Avoid heavily trafficked areas to minimize exposure to vehicle emissions.",
    # Environmental Insights (10 facts)
    "Enviromental Insight: - Air pollution contributes to climate change by increasing greenhouse gas emissions.",
    "Enviromental Insight: - Smog is more prevalent in winter months due to higher fossil fuel consumption for heating.",
    "Enviromental Insight: - Urban greenery, such as trees and parks, naturally helps filter pollutants from the air.",
    "Enviromental Insight: - Industrial sources, including power plants, are major contributors to PM2.5 emissions.",
    "Enviromental Insight: - Vehicle emissions, particularly from diesel engines, are a leading source of NO2.",
    "Enviromental Insight: - Air quality can be significantly worse in valleys where pollutants may become trapped.",
    "Enviromental Insight: - Wildfires can cause dramatic spikes in particulate matter, affecting distant regions.",
    "Enviromental Insight: - Indoor pollution—from cooking, smoking, etc.—can be as harmful as outdoor air pollution.",
    "Enviromental Insight: - Rainfall can temporarily improve air quality by washing pollutants from the atmosphere.",
    "Enviromental Insight: - Transitioning to renewable energy sources, like wind and solar, helps reduce emissions but more importantly, increases the quality of the air we breathe."

"Water Orton Data Insight: - The highest NO2 level recorded so far was 245.65 µg/m³ on 2 June 2025. This exceeds DEFRA's emergency pollution threshold of 200 µg/m³.",

"Water Orton Data Insight: - On 15 May 2025, NO2 levels spiked to 216.54 µg/m³. Sudden peaks like this are usually linked to heavy traffic or stagnant air conditions.",

"Water Orton Data Insight: - On 16 April 2025, NO2 levels reached 199.86 µg/m³ — just below DEFRA's emergency pollution level.",

"Water Orton Data Insight: - The highest PM10 reading recorded so far reached 412.58 µg/m³ on 12 October 2025 — a major particulate spike.",

"Water Orton Data Insight: - The average NO2 level measured across all village sensors is around 33 µg/m³.",

"Water Orton Data Insight: - The Mytton Road sensor records the highest average NO2 levels in the village at roughly 45 µg/m³.",

"Water Orton Data Insight: - Watton Lane records the lowest average NO2 levels among the village sensors at roughly 22 µg/m³.",

"Water Orton Data Insight: - Sensors near main roads tend to record significantly higher NO2 pollution than quieter residential streets.",

"Water Orton Data Insight: - Monitoring multiple locations helps reveal pollution hotspots that a single sensor could miss.",

"Water Orton Data Insight: - Short pollution spikes lasting less than an hour are commonly detected by the village sensors.",

"Water Orton Data Insight: - Pollution levels often increase during commuting hours due to higher vehicle traffic.",

"Water Orton Data Insight: - Rainfall can temporarily improve air quality by washing particles out of the atmosphere.",

"Water Orton Data Insight: - Calm wind conditions can trap pollution near the ground, increasing measured pollutant levels.",

"Water Orton Data Insight: - Even small communities like Water Orton experience measurable air pollution from regional traffic and transport networks.",

"Water Orton Data Insight: - Particulate pollution levels can fluctuate rapidly depending on weather, traffic, and nearby activities.",

"Water Orton Data Insight: - Monitoring air quality locally provides valuable long-term data that national monitoring stations may miss.",

"Water Orton Data Insight: - Some pollution events recorded in the village have approached or exceeded national safety thresholds.",

"Water Orton Data Insight: - Air quality can vary significantly across different parts of the same village depending on nearby roads and pollution sources.",

"Water Orton Data Insight: - Continuous monitoring allows trends to be tracked over months and years, helping identify seasonal pollution patterns.",

"Water Orton Data Insight: - The village monitoring project helps create a detailed local pollution dataset for the community.",

"Water Orton Data Insight: - Traffic emissions remain the primary source of NO2 detected by local sensors.",

"Water Orton Data Insight: - Short bursts of high particulate pollution can occur even when the daily average appears low.",

"Water Orton Data Insight: - Air pollution is often invisible — sensors frequently detect elevated particles even on clear days.",

"Water Orton Data Insight: - Long-term exposure to moderate pollution levels can still impact respiratory health.",

"Water Orton Data Insight: - Temperature inversions during cold weather can trap pollution near ground level.",

"Water Orton Data Insight: - Comparing multiple sensors helps identify the cleanest and most polluted areas of the village.",

"Water Orton Data Insight: - Local monitoring helps communities better understand how pollution behaves in their environment.",

"Water Orton Data Insight: - Pollution spikes are often short-lived but can still impact sensitive individuals.",

"Water Orton Data Insight: - Long-term air monitoring helps measure progress toward cleaner air over time.",

"Water Orton Data Insight: - Community-driven air quality monitoring provides valuable environmental awareness."

"Water Orton Data Insight: - Some NO2 readings recorded in the village have been more than 7x higher than the typical background levels measured across the sensors.",

"Water Orton Data Insight: - The highest pollution spikes recorded so far have occurred during warmer months when atmospheric conditions can trap pollutants near ground level.",

"Water Orton Data Insight: - Local monitoring has revealed that pollution levels can vary dramatically even within a few hundred metres of distance.",

"Water Orton Data Insight: - Some particulate spikes detected by the sensors were over ten times higher than typical daily PM10 readings.",

"Water Orton Data Insight: - Even when the village average appears low, short spikes of pollution can still occur throughout the day.",

"Water Orton Data Insight: - Pollution peaks recorded in the dataset often follow daily traffic patterns across nearby roads and commuter routes.",

"Water Orton Data Insight: - The difference between the cleanest and most polluted sensor locations can exceed 20 µg/m³ in NO2 measurements.",

"Water Orton Data Insight: - Pollution levels recorded overnight are sometimes lower due to reduced traffic activity in the area.",

"Water Orton Data Insight: - Sensors occasionally detect rapid particulate increases caused by passing vehicles or road dust being disturbed.",

"Water Orton Data Insight: - Pollution spikes lasting less than an hour are regularly captured thanks to the high-frequency sensor monitoring.",

"Water Orton Data Insight: - The highest NO2 readings recorded in the dataset occurred during periods of calm wind conditions.",

"Water Orton Data Insight: - Local air quality can change significantly within a single day depending on weather, traffic and atmospheric conditions.",

"Water Orton Data Insight: - The monitoring network across Water Orton helps identify pollution patterns that would otherwise go unnoticed.",

"Water Orton Data Insight: - Some of the lowest pollution readings recorded occurred following rainfall events which help remove airborne particles.",

"Water Orton Data Insight: - Local sensors have detected pollution spikes that were not visible to the naked eye, highlighting the importance of monitoring.",

"Water Orton Data Insight: - The difference between the highest and lowest daily readings across sensors demonstrates how localised pollution can be.",

"Water Orton Data Insight: - Monitoring across multiple locations helps identify pollution hotspots within the village environment.",

"Water Orton Data Insight: - Even moderate increases in traffic flow can produce measurable increases in NO2 levels recorded by roadside sensors.",

"Water Orton Data Insight: - Long-term monitoring allows seasonal pollution patterns to be identified across the village.",

"Water Orton Data Insight: - Community air monitoring helps build a detailed local environmental dataset for future research and awareness."
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
    Returns a dictionary containing specific pollutants for tweet logic.
    """
    sensor_id = sensor["id"]
    url = f"https://airapi.airly.eu/v2/measurements/installation?installationId={sensor_id}"
    headers = {"apikey": AIRLY_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        current_values = data.get("current", {}).get("values", [])

        # Extract specific pollutants for tweet logic
        pm25 = next((x["value"] for x in current_values if x["name"] == "PM2.5"), None)
        pm10 = next((x["value"] for x in current_values if x["name"] == "PM10"), None)
        no2 = next((x["value"] for x in current_values if x["name"] == "NO2"), None)
        no = next((x["value"] for x in current_values if x["name"] == "NO"), None)
        pollutants_tweet = {"PM2.5": pm25, "PM10": pm10, "NO2": no2, "NO": no}



        # Return  pollutants for tweet
        return {
            "sensor_name": sensor["name"],
            "pollutants_tweet": {k: v for k, v in pollutants_tweet.items() if v is not None},
        }
    except requests.RequestException as e:
        logging.error(f"Error fetching data for sensor {sensor_id}: {e}")
        return None



def get_air_quality_for_all_sensors(sensors):
    """
    Aggregates air quality data from all sensors.
    Returns a list of dictionaries, each containing sensor name, and  pollutants.
    """
    all_results = []
    for sensor in sensors:
        result = get_air_quality(sensor)
        if result:
            all_results.append(result)
    return all_results

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
    time_of_day = get_time_of_day()
    results = get_air_quality_for_all_sensors(SENSORS)
    if not results:
        return "Air quality data is unavailable at this time. Please check back later."

    # Use pollutants_tweet for tweet logic
    avg_data_tweet = {}
    max_data_tweet = {"pollutants": {}} #initialise with empty dict to prevent errors.
    max_sensor_name = ""
    for sensor_data in results:
        for pollutant, value in sensor_data["pollutants_tweet"].items():
            avg_data_tweet.setdefault(pollutant, []).append(value)
        if sensor_data['pollutants_tweet'] and max(sensor_data['pollutants_tweet'].values(), default=0) > max(max_data_tweet["pollutants"].values(), default=0):
            max_data_tweet["pollutants"] = sensor_data["pollutants_tweet"]
            max_sensor_name = sensor_data["sensor_name"]

    if avg_data_tweet:
        avg_data = {k: sum(v) / len(v) for k, v in avg_data_tweet.items()}
    else:
        return "Air quality data is unavailable at this time. Please check back later."

    level_avg = determine_pollution_level(avg_data)
    level_max = determine_pollution_level(max_data_tweet["pollutants"])

    overall_level = level_avg
    note = ""
    if level_max != level_avg:
        overall_level = level_max
        note = f" Note: {max_sensor_name} reports higher pollution levels."

    template = random.choice(TEMPLATES[overall_level])

    formatted_time = time_of_day
    if '{Time_of_day}' in template:
        formatted_time = time_of_day[0].upper() + time_of_day[1:]
        tweet = template.format(time_of_day=time_of_day, Time_of_day=formatted_time)
    else:
        tweet = template.format(time_of_day=time_of_day)

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
        logging.info(f"Tweet posted successfully! Tweet ID: {tweet_id}")
    except Exception as e:
        logging.error(f"Error posting tweet: {e}")

def sensor_tweet_job():
    tweet_text = prepare_sensor_tweet()
    logging.info(f"Sensor Tweet: {tweet_text}")
    post_tweet(tweet_text)

def fact_tweet_job():
    tweet_text = prepare_fact_tweet()
    logging.info(f"Fact Tweet: {tweet_text}")
    post_tweet(tweet_text) # Changed "text" to "tweet_text"



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
        logging.info("Within morning window. Sending sensor tweet.")
        sensor_tweet_job()
    elif 12 <= current_hour < 13:
        logging.info("Within midday window. Sending sensor tweet.")
        sensor_tweet_job()
    elif 16 <= current_hour < 17:
        logging.info("Within afternoon window. Sending sensor tweet.")
        sensor_tweet_job()
    elif 19 <= current_hour < 20:
        logging.info("Within evening window. Sending fact tweet.")
        fact_tweet_job()
    else:
        logging.info("Current time not in any tweet window. No tweet will be sent.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()








