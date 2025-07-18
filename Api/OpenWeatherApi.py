import requests
import json
from datetime import datetime
 

def weather(city):
    apiKey ="f18858f8eb05f7654b86088fcdd659f9"

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': apiKey,
        'units': 'metric'  # To get temperature in Celsius
    }

    response = requests.get(base_url, params=params)
    #print(response.status_code)

    if response.status_code == 200:
        data = response.json()
        #print(data)

        jsonData = json.dumps(data, sort_keys=2, indent=2)
        #print(jsonData)
        

        temperature = data['main']['temp']
        min_temperature = data['main']['temp_min']
        max_temperature = data['main']['temp_max']
        sea_level = data['main']['sea_level']
        pressure =  data['main']['pressure']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        sunrise = data['sys']['sunrise']
        sunset = data['sys']['sunset']
        name = data['name']
        
        #convert timestamp to date time
        sunrise = datetime.fromtimestamp(sunrise)
        sunset = datetime.fromtimestamp(sunset)

        return  name, temperature, min_temperature, max_temperature, sea_level, pressure, humidity, description, wind_speed, sunrise, sunset

#name, temperature, min_temperature, max_temperature, sea_level, pressure, humidity, description, wind_speed, sunrise, sunset = weather('jaipur')
#print(sunrise)