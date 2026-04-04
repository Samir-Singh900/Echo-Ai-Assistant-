import requests
import math
from datetime import datetime, timedelta
from textblob import TextBlob
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city, units='metric'):
        try:
            url = f"{self.base_url}/weather?q={city}&appid={self.api_key}&units={units}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed']
                }
            return None
        except Exception as e:
            logger.error(f"Weather service error: {e}")
            return None

class Calculator:
    @staticmethod
    def evaluate(expression):
        try:
            safe_dict = {
                'pi': math.pi,
                'e': math.e,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'exp': math.exp,
                'abs': abs,
                'min': min,
                'max': max,
            }
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"

class TextAnalyzer:
    @staticmethod
    def analyze_sentiment(text):
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                sentiment = "Positive 😊"
            elif polarity < -0.1:
                sentiment = "Negative 😞"
            else:
                sentiment = "Neutral 😐"
            
            return {
                'sentiment': sentiment,
                'polarity': round(polarity, 2),
                'subjectivity': round(subjectivity, 2)
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return None
    
    @staticmethod
    def extract_keywords(text):
        try:
            blob = TextBlob(text)
            words = blob.words
            noun_phrases = blob.noun_phrases
            return {
                'keywords': noun_phrases[:5],
                'word_count': len(words)
            }
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return None

class ReminderManager:
    def __init__(self):
        self.reminders = []
    
    def add_reminder(self, task, hours=1):
        reminder_time = datetime.now() + timedelta(hours=hours)
        self.reminders.append({
            'task': task,
            'time': reminder_time.isoformat(),
            'created': datetime.now().isoformat(),
            'completed': False
        })
        return f"Reminder set for '{task}' in {hours} hour(s)"
    
    def get_pending_reminders(self):
        now = datetime.now()
        pending = [r for r in self.reminders if not r['completed'] and datetime.fromisoformat(r['time']) <= now]
        return pending
    
    def complete_reminder(self, index):
        if 0 <= index < len(self.reminders):
            self.reminders[index]['completed'] = True
            return True
        return False

class URLHandler:
    SAFE_URLS = {
        'google': 'https://google.com',
        'youtube': 'https://youtube.com',
        'github': 'https://github.com',
        'github samir': 'https://github.com/Samir-Singh900',
        'linkedin': 'https://linkedin.com',
        'twitter': 'https://twitter.com',
        'wikipedia': 'https://wikipedia.org'
    }
    
    @staticmethod
    def search_google(query):
        return f"https://www.google.com/search?q={query.replace(' ', '+')}"
    
    @staticmethod
    def search_youtube(query):
        return f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    
    @staticmethod
    def get_safe_url(command):
        for key, url in URLHandler.SAFE_URLS.items():
            if key.lower() in command.lower():
                return url
        return None

def format_response(title, content, icon=""):
    return f"<b>{icon} {title}</b><br>{content}"

def parse_duration(text):
    """Parse duration from text like '5 minutes', '2 hours', etc."""
    import re
    match = re.search(r'(\d+)\s+(minute|hour|day|week)', text.lower())
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        units_map = {'minute': 'minutes', 'hour': 'hours', 'day': 'days', 'week': 'weeks'}
        return {unit: amount}
    return {'hours': 1}  # Default to 1 hour
