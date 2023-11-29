import datetime as dt
import requests
import json
class weather():
    def __init__(self, city):
        self.api_key = "0356412625a34c624b3498c9081a23fc"
        self.city = city
    
    #kelvin to celsius
    def kelvin_to_celsius(self, kelvin):
        celsius = round((kelvin - 273.15),1)
        return celsius

    def input_handling(self, input_city):

        with open('app/data/cities.json') as file:
            cities_data = json.load(file)

        city_list = cities_data['cities']
        for city in city_list:
            if input_city.lower() == city.lower():
                return True
        return False
        
        
    def get_current_weather(self):
        ##Current Data
        #temp
        base_url = "https://api.openweathermap.org/data/2.5/weather?"
        url = base_url + "appid=" + self.api_key +"&q=" + self.city
        self.response = requests.get(url).json()
        
        temp_kelvin = self.response['main']['temp']
        temp_celsius = self.kelvin_to_celsius(temp_kelvin)
        #feel like temp
        feels_like_kelvin = self.response['main']['feels_like']
        feels_like_celsius = self.kelvin_to_celsius(feels_like_kelvin)
        #Weather
        weather = self.response['weather'][0]['main']
        #humidity
        humidity = self.response['main']['humidity']

        current_data = {
            "Temperature": temp_celsius,
            "Feel Like": feels_like_celsius,
            "Weather": weather,
            "Humidity": humidity
        }
        '''
        print(self.city)
        print(f"Temperature: {temp_celsius}°C")
        print(f"Feel Like: {feels_like_celsius}°C")
        print(f"Weather: {weather}")
        print(f"Humidity: {humidity}%")
        print("----------")
        '''
        return current_data

    def get_forecast_weather(self):
        ##Forecast Data
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast?"
        f_url = forecast_url + "appid=" + self.api_key +"&q=" + self.city
        f_response = requests.get(f_url).json()
        #Get 12.00nn data
        daily_forecast = {}
        for item in f_response['list']:
            dt_txt = dt.datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")

            if dt_txt.hour == 12:
                date = dt_txt.date()
                weekday = dt_txt.strftime("%a")
                daily_forecast[date] = (item, weekday)

        forecast_data = {}

        for date, (forecast, weekday) in daily_forecast.items():
            #Date
            Date = dt.datetime.strftime(date, "%Y-%m-%d")
            #future temp
            f_temp_kelvin = forecast['main']['temp']
            f_temp_celsius = self.kelvin_to_celsius(f_temp_kelvin)
            #future feel like temp
            f_feels_like_kelvin = forecast['main']['feels_like']
            f_feels_like_celsius = self.kelvin_to_celsius(f_feels_like_kelvin)
            #Weather
            f_weather = forecast['weather'][0]['main']
            #humidity
            f_humidity = forecast['main']['humidity']

            forecast_data[Date] = {
                "Date": Date,
                "Temperature": f_temp_celsius,
                "Feel Like": f_feels_like_celsius,
                "Weather": f_weather,
                "Humidity": f_humidity
            }

            '''
            print(f"Date: {Date} ({weekday})")
            print(f"Temperature: {f_temp_celsius}°C")
            print(f"Feel Like: {f_feels_like_celsius}°C")
            print(f"Weather: {f_weather}")
            print(f"Humidity: {f_humidity}%")
            print("----------")
            result = {Date:Date}
           '''
        
        return forecast_data

def main():
        city = input("Please enter the City name: ")
        w = weather(city)
        if w.input_handling(city):
            # print(w.get_current_weather())
            print(w.get_forecast_weather())
            return
        else:
            print("Sorry, do not have such city.")   


if __name__ == '__main__':
    main()
