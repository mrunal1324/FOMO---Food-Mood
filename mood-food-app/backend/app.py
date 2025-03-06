from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import asyncio
from model.mood_food_model import MoodFoodRecommender
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the ML model
recommender = MoodFoodRecommender()

# Basic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development'

# Ensure the data directory exists
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USER_DATA_FILE = os.path.join(DATA_DIR, 'user_data.json')

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_user_data(data):
    user_data = load_user_data()
    user_data.append(data)
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f, indent=2)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Mood Food API is running'
    })

@app.route('/api/recommend', methods=['POST'])
async def get_recommendations():
    """Get food recommendations based on mood"""
    try:
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({
                'error': 'Text parameter is required'
            }), 400
            
        # Get recommendations using the ML model
        mood, recommendations, weather = await recommender.get_recommendation(text)
        
        response = {
            'mood': mood,
            'recommendations': recommendations,
            'weather': weather
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/location', methods=['POST'])
def set_location():
    """Set the user's location"""
    try:
        data = request.get_json()
        location = data.get('location')
        
        if not location:
            return jsonify({
                'error': 'Location parameter is required'
            }), 400
            
        recommender.set_location(location)
        return jsonify({
            'message': f'Location updated to {location}'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/weather/toggle', methods=['POST'])
def toggle_weather():
    """Toggle weather-based recommendations"""
    try:
        recommender.toggle_weather()
        status = "enabled" if recommender.user_data['weather_enabled'] else "disabled"
        return jsonify({
            'message': f'Weather-based recommendations {status}'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/save-user-data', methods=['POST'])
def save_user_data_endpoint():
    try:
        data = request.json
        save_user_data(data)
        return jsonify({'message': 'Data saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 