import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
import requests  # For making API calls
import json

# --- IMPORTANT ---
# Paste your three API keys here.
GEMINI_API_KEY = "AIzaSyDkmiG3eUUNl_I37XJSkkw7hjSXTaVEcg8"
WEATHER_API_KEY = "a39a55c6859b46fda7d144100251710"
NEWS_API_KEY = "c3220e6ce884152a0cbce3a736fb8a29"

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)


# --- Define the Python functions that the model can call ---

def get_weather(location: str):
    """
    Finds the current weather for a given location using WeatherAPI.com.
    
    Args:
        location: The city, district, or state. e.g., "Nellore" or "Telangana"
        
    Returns:
        A JSON string with weather data, or a specific error message.
    """
    print(f"Fetching weather for: {location}")
    base_url = "http://api.weatherapi.com/v1/current.json"
    
    # NOTE: The parameter names are 'key' and 'q' for this API
    params = {"key": WEATHER_API_KEY, "q": location, "aqi": "no"}
    
    try:
        response = requests.get(base_url, params=params)
        
        if response.status_code == 401:
            return "Error: Invalid WeatherAPI.com API key."
        elif response.status_code == 400:  # 400 is their code for location not found
            return f"Error: The location '{location}' was not found."
        elif response.status_code == 429:
            return "Error: API rate limit exceeded."
            
        response.raise_for_status()
        return json.dumps(response.json())

    except requests.exceptions.RequestException as e:
        return f"Error: A network problem occurred: {e}"

# Add this function with your others in app.py
def plan_trip(destination: str, duration_days: int, interests: str):
    """
    Acts as a trigger for the AI to generate a travel itinerary.

    Args:
        destination: The city or country to visit.
        duration_days: The length of the trip in days.
        interests: A brief description of what the user likes (e.g., "history, food, beaches").
    Returns:
        A confirmation string that will prompt the AI to generate the plan.
    """
    print(f"Planning a {duration_days}-day trip to {destination} about {interests}")
    # This function just structures the request for the AI.
    # The AI will see this output and then generate the detailed itinerary.
    return (f"Please generate a detailed, day-by-day travel itinerary for a {duration_days}-day trip "
            f"to {destination}, focusing on these interests: {interests}.")
    
def get_news(topic: str):
    """
    Finds top 5 recent news articles for a given topic using GNews API.

    Args:
        topic: The topic to search for, e.g., 'technology' or 'India'

    Returns:
        A JSON string with news articles, or an error message.
    """
    print(f"Fetching news for: {topic}")
    base_url = "https://gnews.io/api/v4/search"
    
    # NOTE: The parameter names are 'q' and 'token'
    params = {"q": topic, "token": NEWS_API_KEY, "max": 5, "lang": "en"}
    
    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 401:
            return "Error: Invalid GNews API key (token)."
        elif response.status_code == 429:
            return "Error: API rate limit exceeded."

        response.raise_for_status()
        return json.dumps(response.json())

    except requests.exceptions.RequestException as e:
        return f"Error: A network problem occurred: {e}"


# --- Teach the model about the functions ---
# Use one of the latest models that supports function calling
model = genai.GenerativeModel(
    'models/gemini-2.5-flash',
    tools=[get_weather, get_news,plan_trip]
)

# Initialize the Flask app
app = Flask(__name__)

# Start a chat session
chat = model.start_chat(enable_automatic_function_calling=True)


# Route for the home page
@app.route('/')
def home():
    """Renders the main chat page."""
    return render_template('index.html')


# Route to handle chat requests
@app.route('/chat', methods=['POST'])
def chat_handler():
    """Handles the chat interaction with the Gemini model."""
    try:
        user_message = request.json['message']
        
        # Send message to the model and get the response
        response = chat.send_message(user_message)
        
        # Return the bot's response
        return jsonify({'response': response.text})
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Sorry, something went wrong.'}), 500


if __name__ == '__main__':
    app.run(debug=True)