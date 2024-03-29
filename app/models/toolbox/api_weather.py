import datetime as dt
import requests
import json
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive
from matplotlib import pyplot as plt
import io
import base64

class Weather:
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
        
    
    # get current weather data from openweathermap API
    def get_current_weather(self):
        ## Current Data
        # temp
        base_url = "https://api.openweathermap.org/data/2.5/weather?"
        url = base_url + "appid=" + self.api_key +"&q=" + self.city
        self.response = requests.get(url).json()
        
        temp_kelvin = self.response['main']['temp']
        temp_celsius = self.kelvin_to_celsius(temp_kelvin)

        # feel like temp
        feels_like_kelvin = self.response['main']['feels_like']
        feels_like_celsius = self.kelvin_to_celsius(feels_like_kelvin)
        # weather
        weather = self.response['weather'][0]['main']
        # humidity
        humidity = self.response['main']['humidity']

        current_data = {
            "Temperature": temp_celsius,
            "Feel Like": feels_like_celsius,
            "Weather": weather,
            "Humidity": humidity
        }

        current_date = dt.datetime.now().strftime("%d/%m")

        data = {
            current_date: current_data
        }
        '''
        print(self.city)
        print(f"Temperature: {temp_celsius}°C")
        print(f"Feel Like: {feels_like_celsius}°C")
        print(f"Weather: {weather}")
        print(f"Humidity: {humidity}%")
        print("----------")
        '''
        return data

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
            Date = dt.datetime.strftime(date, "%d/%m")
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

    @classmethod
    def plot_forecast(cls, weatherDict, cityName):
        dates = []
        temperatures = []
        feels_like_temperatures = []

        for date, data in weatherDict.items():
            dates.append(date)
            temperatures.append(data['Temperature'])
            feels_like_temperatures.append(data['Feel Like'])

        plt.clf()  # Clear the current figure

        # Plotting the Temperature
        plt.plot(dates, temperatures, label='Temperature')

        # Plotting the Feels Like Temperature
        plt.plot(dates, feels_like_temperatures, label='Feels Like Temperature')

        # Add labels and title to the graph
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.title(f'Tempareture of {cityName} in the Coming Five Days')
        plt.legend()

        # Modify x-axis tick labels
        formatted_dates = [date for date in dates]
        plt.xticks(range(len(dates)), formatted_dates)

        # Convert plot to image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # Close the plot
        plt.close()

        return plot_url

def main():
        city = input("Please enter the City name: ")
        w = Weather(city)
        if w.input_handling(city):
            # print(w.get_current_weather())
            print(w.get_forecast_weather())
            return
        else:
            print("Sorry, city not found.")   


if __name__ == '__main__':
    main()
