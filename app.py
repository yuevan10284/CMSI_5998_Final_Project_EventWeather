from flask import Flask, render_template, request, jsonify
from your_script import fetch_weather_data, get_foursquare_data, scrape_events

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', 'coffee')
    location = request.form.get('location', 'Los Angeles, CA')
    places = get_foursquare_data(query=query, near=location, limit=10)
    weather_data = fetch_weather_data()
    return jsonify({
        'places': places,
        'weather': weather_data
    })

@app.route('/explore')
def explore():
    events = scrape_events(limit=10)
    weather_data = fetch_weather_data()
    return render_template('explore.html', events=events, weather=weather_data)

@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    weather_data = fetch_weather_data(lat, lon)
    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)