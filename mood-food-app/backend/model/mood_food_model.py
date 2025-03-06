import os
from typing import Dict, List, Tuple
import random
import json
import datetime
import requests
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Load environment variables
load_dotenv()

class MoodFoodRecommender:
    def __init__(self):
        # Initialize sentiment analyzer using Transformers
        print("Loading emotion detection model...")
        self.sentiment_analyzer = pipeline(
            "text-classification",
            model="SamLowe/roberta-base-go_emotions",
            top_k=3
        )
        
        # Initialize data storage
        self.data_file = Path("user_data.json")
        self.user_data = self.load_user_data()
        
        # Negation words that can reverse the emotion
        self.negation_words = ['not', "don't", "doesn't", "didn't", "won't", "wouldn't", "couldn't", "can't", "never", "no"]
        
        # Emotional context phrases
        self.emotional_context = {
            'lazy': {
                'positive_context': ['relaxing', 'chilling', 'taking it easy', 'unwinding'],
                'negative_context': ['procrastinating', 'wasting time', 'being unproductive']
            },
            'romantic': {
                'positive_context': ['date night', 'special occasion', 'quality time', 'together'],
                'negative_context': ['lonely', 'missing someone', 'long distance']
            },
            'happy': {
                'positive_context': ['celebration', 'achievement', 'success', 'good news'],
                'negative_context': ['trying to be happy', 'forcing a smile', 'pretending']
            },
            'sad': {
                'positive_context': ['missing someone', 'memories', 'nostalgia'],
                'negative_context': ['depression', 'hopelessness', 'despair']
            },
            'energetic': {
                'positive_context': ['workout', 'exercise', 'activity', 'movement'],
                'negative_context': ['hyper', 'restless', 'can\'t sit still']
            },
            'stressed': {
                'positive_context': ['busy', 'productive', 'challenging'],
                'negative_context': ['overwhelmed', 'burned out', 'exhausted']
            },
            'productive': {
                'positive_context': ['accomplishment', 'progress', 'achievement'],
                'negative_context': ['overworking', 'burnout', 'exhaustion']
            }
        }
        
        # Weatherbit API configuration
        self.weatherbit_api_key = os.getenv('WEATHERBIT_API_KEY')
        if not self.weatherbit_api_key:
            print("Warning: WEATHERBIT_API_KEY not found in environment variables.")
            print("Weather-based recommendations will be disabled.")
            self.user_data['weather_enabled'] = False
            self.save_user_data()
        
        self.weatherbit_base_url = "https://api.weatherbit.io/v2.0"
        
        # Enhanced food categories and their mood associations
        self.food_mood_mapping = {
            'happy': [
                'Colorful Mediterranean salad with feta and olives',
                'Fresh fruit smoothie bowl with granola',
                'Light pasta primavera with fresh vegetables',
                'Grilled chicken with mango salsa',
                'Rainbow sushi roll'
            ],
            'sad': [
                'Creamy mac and cheese',
                'Warm chicken noodle soup',
                'Chocolate lava cake',
                'Mashed potatoes with gravy',
                'Warm bread with butter'
            ],
            'energetic': [
                'Quinoa power bowl with grilled chicken',
                'Whole grain toast with avocado and eggs',
                'Fresh vegetable stir-fry with tofu',
                'Protein-rich Greek yogurt parfait',
                'Grilled salmon with brown rice'
            ],
            'tired': [
                'Energy-boosting green smoothie',
                'Mixed nuts and dried fruits trail mix',
                'Green tea with honey',
                'Banana and peanut butter toast',
                'Dark chocolate covered almonds'
            ],
            'stressed': [
                'Calming chamomile tea with honey',
                'Dark chocolate with sea salt',
                'Lavender-infused cookies',
                'Green tea and matcha latte',
                'Anti-stress berry smoothie'
            ],
            'romantic': [
                'Classic spaghetti carbonara',
                'Chocolate-covered strawberries',
                'French onion soup',
                'Red wine braised beef',
                'Crème brûlée'
            ],
            'productive': [
                'Brain-boosting blueberry oatmeal',
                'Grilled chicken with quinoa',
                'Salmon with sweet potato',
                'Greek yogurt with granola',
                'Mixed berry protein smoothie'
            ],
            'lazy': [
                'One-pot pasta dish',
                'Sheet pan chicken and vegetables',
                '5-minute microwave mug cake',
                'Quick tuna salad wrap',
                'Easy breakfast burrito'
            ],
            'neutral': [
                'Classic club sandwich',
                'Caesar salad with grilled chicken',
                'Margherita pizza',
                'Turkey and cheese wrap',
                'Mixed green salad'
            ]
        }
        
        # Emotion to mood mapping
        self.emotion_mood_mapping = {
            # Positive emotions
            'joy': 'happy',
            'love': 'romantic',
            'pride': 'productive',
            'gratitude': 'happy',
            'optimism': 'productive',
            'amusement': 'happy',
            'excitement': 'energetic',
            'desire': 'romantic',
            'admiration': 'romantic',
            'relief': 'happy',
            
            # Negative emotions
            'sadness': 'sad',
            'anger': 'stressed',
            'fear': 'stressed',
            'disgust': 'stressed',
            'remorse': 'sad',
            'grief': 'sad',
            'anxiety': 'stressed',
            'nervousness': 'stressed',
            'disappointment': 'sad',
            'embarrassment': 'stressed',
            
            # Neutral/Complex emotions
            'surprise': 'energetic',
            'confusion': 'stressed',
            'curiosity': 'energetic',
            'boredom': 'lazy',
            'tiredness': 'tired',
            'fatigue': 'tired',
            'exhaustion': 'tired',
            'neutral': 'neutral',
            'calmness': 'neutral',
            'peace': 'happy'
        }
        
        # Weather-based food adjustments
        self.weather_food_adjustments = {
            'hot': ['cold', 'refreshing', 'light', 'cooling'],
            'cold': ['warm', 'hearty', 'hot', 'comforting'],
            'rainy': ['warm', 'comforting', 'indoor'],
            'sunny': ['fresh', 'light', 'outdoor-friendly']
        }
        
        # Enhanced mood keyword mapping with context and intensity
        self.mood_keywords = {
            'lazy': {
                'keywords': ['lazy', 'tired', 'exhausted', 'fatigued', 'sleepy', 'drowsy', 'unmotivated', 'sluggish'],
                'intensifiers': ['very', 'extremely', 'really', 'so'],
                'context': ['couch', 'bed', 'relax', 'rest', 'nap']
            },
            'romantic': {
                'keywords': ['romantic', 'love', 'passionate', 'intimate', 'amorous', 'romance', 'date'],
                'intensifiers': ['very', 'deeply', 'truly', 'madly'],
                'context': ['partner', 'date', 'candlelight', 'dinner', 'special']
            },
            'happy': {
                'keywords': ['happy', 'joyful', 'cheerful', 'glad', 'delighted', 'excited', 'thrilled', 'elated'],
                'intensifiers': ['very', 'extremely', 'really', 'so'],
                'context': ['great', 'wonderful', 'amazing', 'fantastic']
            },
            'sad': {
                'keywords': ['sad', 'unhappy', 'depressed', 'down', 'gloomy', 'miserable', 'heartbroken'],
                'intensifiers': ['very', 'extremely', 'really', 'so'],
                'context': ['cry', 'miss', 'lonely', 'alone']
            },
            'energetic': {
                'keywords': ['energetic', 'energized', 'active', 'vibrant', 'lively', 'dynamic', 'peppy'],
                'intensifiers': ['very', 'extremely', 'really', 'so'],
                'context': ['workout', 'exercise', 'run', 'play']
            },
            'stressed': {
                'keywords': ['stressed', 'anxious', 'worried', 'tense', 'nervous', 'overwhelmed', 'pressured'],
                'intensifiers': ['very', 'extremely', 'really', 'so'],
                'context': ['deadline', 'work', 'pressure', 'anxiety']
            },
            'productive': {
                'keywords': ['productive', 'focused', 'motivated', 'determined', 'efficient', 'accomplished'],
                'intensifiers': ['very', 'extremely', 'really', 'so'],
                'context': ['work', 'task', 'project', 'goal']
            },
            'neutral': {
                'keywords': ['neutral', 'okay', 'fine', 'alright', 'normal', 'average', 'regular'],
                'intensifiers': [],
                'context': ['usual', 'typical', 'standard']
            }
        }
        
        # Compound emotion patterns
        self.compound_patterns = {
            'romantic': [
                ('love', 'happy'),
                ('desire', 'excitement'),
                ('admiration', 'joy')
            ],
            'stressed': [
                ('anxiety', 'fear'),
                ('anger', 'frustration'),
                ('worry', 'nervousness')
            ],
            'productive': [
                ('pride', 'determination'),
                ('focus', 'motivation'),
                ('accomplishment', 'satisfaction')
            ]
        }
        
        # Enhanced seasonal food preferences
        self.seasonal_preferences = {
            'spring': {
                'temperature_range': (45, 70),
                'preferred_styles': ['light', 'fresh', 'crisp', 'grilled'],
                'ingredients': ['asparagus', 'strawberries', 'peas', 'radishes', 'spring greens'],
                'avoid': ['heavy', 'rich', 'warm']
            },
            'summer': {
                'temperature_range': (70, 95),
                'preferred_styles': ['cold', 'refreshing', 'light', 'grilled'],
                'ingredients': ['tomatoes', 'cucumber', 'watermelon', 'berries', 'fresh herbs'],
                'avoid': ['hot', 'heavy', 'baked']
            },
            'fall': {
                'temperature_range': (45, 70),
                'preferred_styles': ['warm', 'roasted', 'comforting'],
                'ingredients': ['pumpkin', 'apples', 'squash', 'cranberries', 'nuts'],
                'avoid': ['cold', 'light', 'raw']
            },
            'winter': {
                'temperature_range': (20, 45),
                'preferred_styles': ['warm', 'hearty', 'comforting', 'hot'],
                'ingredients': ['root vegetables', 'winter squash', 'citrus', 'dark greens'],
                'avoid': ['cold', 'raw', 'light']
            }
        }
        
        # Temperature-based adjustments
        self.temperature_adjustments = {
            'very_cold': {
                'range': (-float('inf'), 32),
                'multipliers': {
                    'warm': 1.5,
                    'hot': 1.3,
                    'cold': 0.5,
                    'raw': 0.3
                }
            },
            'cold': {
                'range': (32, 45),
                'multipliers': {
                    'warm': 1.3,
                    'hot': 1.2,
                    'cold': 0.7,
                    'raw': 0.5
                }
            },
            'mild': {
                'range': (45, 70),
                'multipliers': {
                    'warm': 1.1,
                    'hot': 1.0,
                    'cold': 1.0,
                    'raw': 1.0
                }
            },
            'warm': {
                'range': (70, 85),
                'multipliers': {
                    'warm': 0.8,
                    'hot': 0.7,
                    'cold': 1.2,
                    'raw': 1.3
                }
            },
            'hot': {
                'range': (85, float('inf')),
                'multipliers': {
                    'warm': 0.6,
                    'hot': 0.5,
                    'cold': 1.5,
                    'raw': 1.5
                }
            }
        }

    def load_user_data(self) -> Dict:
        """Load user data from file or create new if doesn't exist."""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {
            'preferences': {},
            'history': [],
            'favorite_foods': [],
            'location': 'London',  # Default location
            'weather_enabled': True
        }

    def save_user_data(self):
        """Save user data to file."""
        with open(self.data_file, 'w') as f:
            json.dump(self.user_data, f, indent=4)

    def get_default_weather(self) -> Dict:
        """Get default weather data based on current season and time of day."""
        current_time = datetime.datetime.now()
        current_month = current_time.month
        current_hour = current_time.hour
        
        # Base temperature by season
        if 3 <= current_month <= 5:  # Spring
            base_temp = 65
            condition = 'mild'
        elif 6 <= current_month <= 8:  # Summer
            base_temp = 80
            condition = 'sunny'
        elif 9 <= current_month <= 11:  # Fall
            base_temp = 55
            condition = 'cool'
        else:  # Winter
            base_temp = 35
            condition = 'cold'
            
        # Adjust temperature based on time of day
        if 5 <= current_hour < 12:  # Morning
            base_temp -= 5
        elif 12 <= current_hour < 17:  # Afternoon
            base_temp += 5
        elif 17 <= current_hour < 22:  # Evening
            base_temp -= 2
        else:  # Night
            base_temp -= 8
            
        # Determine weather conditions
        is_hot = base_temp > 75
        is_cold = base_temp < 45
        is_rainy = False  # Default to false for default weather
        is_sunny = True   # Default to true for default weather
        
        return {
            'temperature': base_temp,
            'condition': condition,
            'is_hot': is_hot,
            'is_cold': is_cold,
            'is_rainy': is_rainy,
            'is_sunny': is_sunny,
            'humidity': 60,  # Default humidity
            'wind_speed': 5  # Default wind speed
        }

    async def get_weather(self, location: str) -> Dict:
        """Get current weather conditions for the location using Weatherbit API."""
        if not self.user_data.get('weather_enabled', True) or not self.weatherbit_api_key:
            return self.get_default_weather()
            
        try:
            # Get current weather data
            params = {
                'city': location,
                'key': self.weatherbit_api_key,
                'units': 'I',  # Imperial units (Fahrenheit)
                'include': 'minutely'  # Include detailed weather data
            }
            
            response = requests.get(f"{self.weatherbit_base_url}/current", params=params)
            response.raise_for_status()
            weather_data = response.json()
            
            if not weather_data.get('data'):
                raise Exception("No weather data found for location")
                
            current = weather_data['data'][0]
            
            # Extract relevant weather information
            temp = current['temp']
            precip = current.get('precip', 0)
            clouds = current.get('clouds', 0)
            humidity = current.get('rh', 60)  # Relative humidity
            wind_speed = current.get('wind_spd', 5)  # Wind speed in mph
            weather_code = current['weather']['code']
            
            # Enhanced weather condition detection
            weather_conditions = {
                'clear': [800],
                'partly_cloudy': [801, 802],
                'cloudy': [803, 804],
                'light_rain': [500, 501, 502, 503],
                'heavy_rain': [504, 505, 506, 507],
                'thunderstorm': [200, 201, 202, 230, 231, 232, 233],
                'snow': [600, 601, 602, 610, 611, 612, 621, 622, 623],
                'sleet': [700, 711, 721, 731, 741, 751],
                'fog': [701, 711, 721, 731, 741, 751]
            }
            
            # Determine weather condition
            condition = 'unknown'
            for cond, codes in weather_conditions.items():
                if weather_code in codes:
                    condition = cond
                    break
            
            # Enhanced temperature categorization
            temp_category = self.get_temperature_category(temp)
            
            # Determine weather states with more nuanced thresholds
            is_hot = temp > 80 or (temp > 75 and humidity > 70)  # Consider humidity for hot conditions
            is_cold = temp < 40 or (temp < 45 and wind_speed > 15)  # Consider wind chill
            is_rainy = (
                precip > 0 or 
                clouds > 70 or 
                weather_code in [500, 501, 502, 503, 504, 505, 506, 507, 200, 201, 202, 230, 231, 232, 233]
            )
            is_sunny = (
                clouds < 30 and 
                precip == 0 and 
                weather_code in [800, 801] and
                humidity < 80  # Consider humidity for sunny conditions
            )
            
            # Adjust temperature based on wind chill or heat index
            feels_like = temp
            if is_cold and wind_speed > 5:
                # Simple wind chill calculation
                feels_like = temp - (wind_speed * 0.1)
            elif is_hot and humidity > 60:
                # Simple heat index calculation
                feels_like = temp + (humidity * 0.1)
            
            return {
                'temperature': temp,
                'feels_like': feels_like,
                'condition': condition,
                'is_hot': is_hot,
                'is_cold': is_cold,
                'is_rainy': is_rainy,
                'is_sunny': is_sunny,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'clouds': clouds,
                'precip': precip
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Weather API error: {e}")
            print("Using default weather based on current season...")
            return self.get_default_weather()
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Using default weather based on current season...")
            return self.get_default_weather()

    def set_location(self, location: str):
        """Set the user's location and validate it with Weatherbit API."""
        if not self.weatherbit_api_key:
            print("Error: Weatherbit API key not configured. Please set WEATHERBIT_API_KEY in your .env file.")
            return
            
        try:
            # Test the location with Weatherbit API
            params = {
                'city': location,
                'key': self.weatherbit_api_key,
                'units': 'I'  # Imperial units (Fahrenheit)
            }
            
            response = requests.get(f"{self.weatherbit_base_url}/current", params=params)
            response.raise_for_status()
            weather_data = response.json()
            
            if not weather_data.get('data'):
                raise Exception("Location not found")
                
            self.user_data['location'] = location
            self.save_user_data()
            print(f"Location updated to: {location}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to weather service: {e}")
            print("Please check your internet connection and API key.")
        except Exception as e:
            print(f"Error validating location: {e}")
            print("Please enter a valid city name.")

    def toggle_weather(self):
        """Toggle weather-based recommendations on/off."""
        self.user_data['weather_enabled'] = not self.user_data.get('weather_enabled', True)
        self.save_user_data()
        status = "enabled" if self.user_data['weather_enabled'] else "disabled"
        print(f"Weather-based recommendations {status}")

    def analyze_mood(self, text: str) -> Dict:
        """Analyze the mood from text input using enhanced emotion detection."""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Check for negation
        has_negation = any(word in self.negation_words for word in words)
        
        # Check for direct mood keywords with context and intensity
        best_match = None
        best_intensity = 0
        
        for mood, data in self.mood_keywords.items():
            # Check for keywords
            keyword_found = any(keyword in text_lower for keyword in data['keywords'])
            
            if keyword_found:
                # Calculate intensity based on intensifiers and context
                intensity = 0.7  # Base intensity for keyword match
                
                # Check for intensifiers
                for word in words:
                    if word in data['intensifiers']:
                        intensity = min(1.0, intensity + 0.2)
                
                # Check for context words
                context_matches = sum(1 for word in words if word in data['context'])
                if context_matches > 0:
                    intensity = min(1.0, intensity + (0.1 * context_matches))
                
                # Check for emotional context phrases
                if mood in self.emotional_context:
                    for phrase in self.emotional_context[mood]['positive_context']:
                        if phrase in text_lower:
                            intensity = min(1.0, intensity + 0.15)
                    for phrase in self.emotional_context[mood]['negative_context']:
                        if phrase in text_lower:
                            intensity = max(0.0, intensity - 0.15)
                
                # Apply negation effect
                if has_negation:
                    intensity = 1.0 - intensity
                    # Map to opposite mood if possible
                    opposite_moods = {
                        'happy': 'sad',
                        'sad': 'happy',
                        'energetic': 'tired',
                        'tired': 'energetic',
                        'stressed': 'calm',
                        'productive': 'lazy',
                        'lazy': 'productive'
                    }
                    if mood in opposite_moods:
                        mood = opposite_moods[mood]
                
                if intensity > best_intensity:
                    best_intensity = intensity
                    best_match = {
                        "emotion_scores": [],
                        "mood": mood,
                        "intensity": intensity,
                        "top_emotion": mood,
                        "secondary_emotions": []
                    }
        
        if best_match and best_intensity > 0.5:
            return best_match
        
        # If no direct keyword match or low confidence, use emotion detection model
        emotion_scores = self.sentiment_analyzer(text)
        
        # Get top emotions and their scores
        top_emotions = []
        for score in emotion_scores[0]:
            emotion = score['label'].lower()
            confidence = score['score']
            # Apply negation effect to confidence
            if has_negation:
                confidence = 1.0 - confidence
            top_emotions.append((emotion, confidence))
        
        # Sort emotions by confidence
        top_emotions.sort(key=lambda x: x[1], reverse=True)
        
        # Check for compound emotions
        for mood, patterns in self.compound_patterns.items():
            for pattern in patterns:
                if all(any(e[0] == p for e in top_emotions) for p in pattern):
                    return {
                        "emotion_scores": emotion_scores[0],
                        "mood": mood,
                        "intensity": max(e[1] for e in top_emotions),
                        "top_emotion": mood,
                        "secondary_emotions": [e[0] for e in top_emotions if e[0] not in pattern]
                    }
        
        # Get the top emotion
        top_emotion, intensity = top_emotions[0]
        
        # Map emotion to mood with confidence threshold
        mood = self.emotion_mood_mapping.get(top_emotion, 'neutral')
        
        # If confidence is low or emotion isn't mapped, try secondary emotions
        if intensity < 0.6 or mood == 'neutral':
            for emotion, conf in top_emotions[1:]:
                if conf > 0.5:  # Only consider secondary emotions with decent confidence
                    mapped_mood = self.emotion_mood_mapping.get(emotion)
                    if mapped_mood and mapped_mood != 'neutral':
                        mood = mapped_mood
                        intensity = conf
                        top_emotion = emotion
                        break
        
        return {
            "emotion_scores": emotion_scores[0],
            "mood": mood,
            "intensity": intensity,
            "top_emotion": top_emotion,
            "secondary_emotions": [e[0] for e in top_emotions[1:]]
        }

    def get_season(self, month: int) -> str:
        """Determine the current season based on month."""
        if 3 <= month <= 5:
            return 'spring'
        elif 6 <= month <= 8:
            return 'summer'
        elif 9 <= month <= 11:
            return 'fall'
        else:
            return 'winter'

    def get_temperature_category(self, temperature: float) -> str:
        """Get temperature category based on current temperature with more granular ranges."""
        if temperature < 32:
            return 'very_cold'
        elif 32 <= temperature < 45:
            return 'cold'
        elif 45 <= temperature < 60:
            return 'cool'
        elif 60 <= temperature < 75:
            return 'mild'
        elif 75 <= temperature < 85:
            return 'warm'
        else:
            return 'hot'

    def calculate_food_score(self, food: str, temperature: float, season: str) -> float:
        """Calculate a score for a food item based on temperature and season."""
        score = 1.0  # Base score
        
        # Get temperature category and adjustments
        temp_category = self.get_temperature_category(temperature)
        temp_multipliers = self.temperature_adjustments[temp_category]['multipliers']
        
        # Get seasonal preferences
        season_prefs = self.seasonal_preferences[season]
        
        # Check food characteristics against temperature preferences
        food_lower = food.lower()
        
        # Apply temperature-based multipliers
        if any(word in food_lower for word in ['warm', 'hot', 'heated']):
            score *= temp_multipliers['warm']
        if any(word in food_lower for word in ['cold', 'chilled', 'cool']):
            score *= temp_multipliers['cold']
        if any(word in food_lower for word in ['raw', 'fresh', 'crisp']):
            score *= temp_multipliers['raw']
        
        # Apply seasonal preferences
        for style in season_prefs['preferred_styles']:
            if style in food_lower:
                score *= 1.2
        for ingredient in season_prefs['ingredients']:
            if ingredient in food_lower:
                score *= 1.1
        for avoid in season_prefs['avoid']:
            if avoid in food_lower:
                score *= 0.8
        
        return score

    def get_food_recommendations(self, mood: str, weather: Dict = None) -> List[str]:
        """Get food recommendations based on mood, weather, and season."""
        # Get base recommendations from mapping
        recommendations = self.food_mood_mapping.get(mood, [])
        
        if weather and self.user_data.get('weather_enabled', True):
            # Get current season
            current_month = datetime.datetime.now().month
            season = self.get_season(current_month)
            
            # Calculate scores for each recommendation
            scored_recommendations = []
            for food in recommendations:
                score = self.calculate_food_score(food, weather['temperature'], season)
                scored_recommendations.append((food, score))
            
            # Sort by score
            scored_recommendations.sort(key=lambda x: x[1], reverse=True)
            
            # Consider user preferences
            if mood in self.user_data['preferences']:
                preferred_foods = self.user_data['preferences'][mood]
                for food, score in scored_recommendations:
                    if any(pf in food.lower() for pf in preferred_foods):
                        score *= 1.2  # Boost score for preferred foods
            
            # Get top 3 recommendations
            recommendations = [food for food, _ in scored_recommendations[:3]]
        
        # Ensure we have at least 3 recommendations
        if len(recommendations) < 3:
            all_mood_foods = self.food_mood_mapping.get(mood, [])
            additional = [r for r in all_mood_foods if r not in recommendations]
            recommendations.extend(additional)
        
        # Randomly select 3 recommendations if we have more
        if len(recommendations) > 3:
            recommendations = random.sample(recommendations, 3)
        
        return recommendations

    def update_user_preferences(self, mood: str, food: str):
        """Update user preferences based on their mood and food choice."""
        if mood not in self.user_data['preferences']:
            self.user_data['preferences'][mood] = []
        
        # Add food to preferences if not already present
        if food not in self.user_data['preferences'][mood]:
            self.user_data['preferences'][mood].append(food)
        
        # Update history
        self.user_data['history'].append({
            'date': datetime.datetime.now().isoformat(),
            'mood': mood,
            'food': food
        })
        
        # Save updated data
        self.save_user_data()

    async def get_recommendation(self, text: str) -> Tuple[str, List[str], Dict]:
        """Get mood analysis and food recommendations for input text."""
        # Analyze mood
        mood_analysis = self.analyze_mood(text)
        mood = mood_analysis['mood']
        
        # Get weather
        weather = await self.get_weather(self.user_data['location'])
        
        # Get recommendations
        recommendations = self.get_food_recommendations(mood, weather)
        
        # Print detailed emotion analysis
        print(f"\nEmotion Analysis:")
        print(f"Primary Emotion: {mood_analysis['top_emotion'].capitalize()} ({mood_analysis['intensity']:.2f})")
        if mood_analysis['secondary_emotions']:
            print(f"Secondary Emotions: {', '.join(mood_analysis['secondary_emotions'])}")
        
        return mood, recommendations, weather 