import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')

def get_aqi_data(city):
    api_url = f'https://api.api-ninjas.com/v1/airquality?city={city}'
    headers = {'X-Api-Key': API_KEY}
    response = requests.get(api_url, headers=headers)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None