import os
import json
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Load API keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables!")

# --- Configure Gemini ---
genai.configure(api_key=GEMINI_API_KEY)

# --- Define callable tools ---
def get_weather(location: str):
    """Get current weather using WeatherAPI.com"""
    print(f"Fetching weather for: {location}")
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": WEATHER_API_KEY, "q": location, "aqi": "no"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return f"The weather in {data['location']['name']} is {data['current']['condition']['text']} with {data['current']['temp_c']}°C."
    except Exception as e:
        return f"Error fetching weather: {e}"

def get_news(topic: str):
    """Get top 5 news articles using GNews API"""
    print(f"Fetching news for: {topic}")
    base_url = "https://gnews.io/api/v4/search"
    params = {"q": topic, "token": NEWS_API_KEY, "max": 5, "lang": "en"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        if not articles:
            return f"No recent news found for '{topic}'."
        result = "\n".join([f"📰 {a['title']} ({a['source']['name']})" for a in articles[:5]])
        return f"Here are top news on {topic}:\n{result}"
    except Exception as e:
        return f"Error fetching news: {e}"

def plan_trip(destination: str, duration_days: int, interests: str):
    """Generate a trip plan request for Gemini"""
    print(f"Planning a {duration_days}-day trip to {destination}")
    return (f"Please create a {duration_days}-day travel itinerary to {destination}, "
            f"focused on {interests}. Include recommendations for activities, places, and food.")

# --- Initialize Gemini Model ---
# 'models/gemini-1.5-flash-latest' works on current API
model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash",
    tools=[get_weather, get_news, plan_trip]
)

chat = model.start_chat(enable_automatic_function_calling=True)

# --- Flask App Setup ---
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_handler():
    try:
        user_message = request.json['message']
        response = chat.send_message(user_message)
        return jsonify({'response': response.text})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
