import argparse
import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='Tourism and Cultural Event Insights')
    parser.add_argument('--static', nargs='?', const='static_data', help='Static Mode: Provide path to static dataset(s)')
    parser.add_argument('--scrape', action='store_true', help='Scrape Mode: Perform scraping and API requests for a few select elements')

    args = parser.parse_args()

    if args.static:
        static_mode(args.static)
    elif args.scrape:
        scrape_mode()
    else:
        default_mode()

def fetch_weather_data():
    print("Fetching weather data from OpenWeatherMap...")
    
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
    if not OPENWEATHERMAP_API_KEY:
        print("Error: OpenWeatherMap API key not found in environment variables")
        return {}
        
    # Los Angeles coordinates
    lat = 34.0522
    lon = -118.2437
    
    # Using v2.5 API endpoint instead of v3.0
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        weather_data = response.json()
        
        # Extract current weather from first entry
        current_weather = {
            'temperature': weather_data['list'][0]['main']['temp'],
            'description': weather_data['list'][0]['weather'][0]['description'],
            'humidity': weather_data['list'][0]['main']['humidity'],
            'wind_speed': weather_data['list'][0]['wind']['speed']
        }
        
        # Extract daily forecast (every 24 hours)
        daily_forecast = []
        for day in weather_data['list'][::8]:  # Every 8th entry is a new day (3-hour intervals)
            daily_forecast.append({
                'date': datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d'),
                'temperature': {
                    'day': day['main']['temp'],
                    'min': day['main']['temp_min'],
                    'max': day['main']['temp_max']
                },
                'description': day['weather'][0]['description'],
                'humidity': day['main']['humidity'],
                'wind_speed': day['wind']['speed']
            })
        
        weather_info = {
            'current': current_weather,
            'daily_forecast': daily_forecast
        }
        
        print("Successfully fetched weather data")
        return weather_info
        
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return {}

def get_foursquare_data(query="coffee", near="Los Angeles, CA", limit=5):
    """
    Fetch data from Foursquare API based on user-provided query and location.
    
    Args:
        query (str): The search query, e.g., "coffee".
        near (str): The location to search near, e.g., "San Marino, CA".
        limit (int): The number of results to fetch.
    
    Returns:
        list: A list of dictionaries containing place information.
    """
    print(f"Fetching data from Foursquare API for query '{query}' near '{near}'...")
    FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")
    
    # Construct the URL dynamically based on query and near
    url = f"https://api.foursquare.com/v3/places/search?query={query}&near={near.replace(' ', '%20')}&limit={limit}"

    headers = {
        "accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        places = []
        for place in data.get('results', []):
            places.append({
                'Name': place.get('name'),
                'Address': place.get('location', {}).get('formatted_address', 'N/A'),
                'Category': place.get('categories', [{}])[0].get('name', 'N/A')
            })
        print(f"Successfully fetched {len(places)} places from Foursquare.")
        return places
    except requests.RequestException as e:
        print(f"Error fetching Foursquare data: {e}")
        return []


def scrape_events(limit=5):
    """Scrape events from AllEvents.in for Los Angeles."""
    print("Scraping data from AllEvents.in...")
    URL = "https://allevents.in/los%20angeles"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        events = []

        # Select the event cards
        event_cards = soup.select('li.event-card')[:limit]
        if not event_cards:
            print("No event data found. The structure of the page might have changed.")
            return []

        # Extract details for each event
        for event in event_cards:
            title = event.select_one('div.title h3').text.strip() if event.select_one('div.title h3') else 'No title'
            location = event.select_one('div.subtitle').text.strip() if event.select_one('div.subtitle') else 'No location'
            date = event.select_one('div.date').text.strip() if event.select_one('div.date') else 'No date'
            events.append({'Title': title, 'Location': location, 'Date': date})

        print(f"Successfully scraped {len(events)} events.")
        return events
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def save_static_data(weather_data, foursquare_data, events_data):
    """
    Save fetched data to static files.
    
    Args:
        weather_data (dict): Weather data.
        foursquare_data (list): List of places data.
        events_data (list): List of events data.
    """
    print("Saving data to static files...")
    STATIC_DATASET_DIR = 'static_data'
    os.makedirs(STATIC_DATASET_DIR, exist_ok=True)
    
    # Save weather data
    weather_file = os.path.join(STATIC_DATASET_DIR, 'weather_data.json')
    with open(weather_file, 'w') as f:
        json.dump(weather_data, f, indent=4)
    print(f"Weather data saved to {weather_file}")

    # Save Foursquare data to CSV
    foursquare_file = os.path.join(STATIC_DATASET_DIR, 'foursquare_data.csv')
    df_places = pd.DataFrame(foursquare_data)
    # Ensure proper formatting
    df_places.to_csv(foursquare_file, index=False, columns=['Name', 'Address', 'Category'])
    print(f"Foursquare data saved to {foursquare_file}")

    # Save events data to CSV
    events_file = os.path.join(STATIC_DATASET_DIR, 'events_data.csv')
    df_events = pd.DataFrame(events_data)
    df_events.to_csv(events_file, index=False)
    print(f"Events data saved to {events_file}")

def print_data_samples(weather_data, foursquare_data, events_data):
    print("\nSample Data:")
    print("\nWeather Data:")
    print(json.dumps(weather_data, indent=4))

    print("\nFoursquare Data (first 5 places):")
    for place in foursquare_data[:5]:
        print(json.dumps(place, indent=4))

    print("\nEvents Data (first 5 events):")
    for event in events_data[:5]:
        print(json.dumps(event, indent=4))

def default_mode():
    print("Running in Default Mode...")
    weather_data = fetch_weather_data()
    foursquare_data = get_foursquare_data(limit=10)
    events_data = scrape_events(limit=10)

    # Save data to static files
    save_static_data(weather_data, foursquare_data, events_data)

    # Print sample data
    print_data_samples(weather_data, foursquare_data, events_data)

def scrape_mode():
    print("Running in Scrape Mode...")
    weather_data = fetch_weather_data()
    foursquare_data = get_foursquare_data(limit=5)
    events_data = scrape_events(limit=5)

    # Print sample data
    print_data_samples(weather_data, foursquare_data, events_data)

def static_mode(static_path):
    print("Running in Static Mode...")
    # Assume static_path is a directory containing the static data files
    weather_file = os.path.join(static_path, 'weather_data.json')
    foursquare_file = os.path.join(static_path, 'foursquare_data.csv')
    events_file = os.path.join(static_path, 'events_data.csv')

    # Load data
    try:
        with open(weather_file, 'r') as f:
            weather_data = json.load(f)
        df_places = pd.read_csv(foursquare_file)
        df_events = pd.read_csv(events_file)
        # Convert DataFrame to list of dicts
        foursquare_data = df_places.to_dict('records')
        events_data = df_events.to_dict('records')
    except FileNotFoundError as e:
        print(f"Error loading static data: {e}")
        return

    # Print sample data
    print_data_samples(weather_data, foursquare_data, events_data)

if __name__ == '__main__':
    main()
