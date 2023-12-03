### Adv-Py-Domain Tripping 

## Overview
Tripping is a web application designed to advance The trip-planning experience.
    - **Trip creating**: create trip with your friends
        - Map showcase: showing the city map of the location
        - Weather forecast: forecast the weather of the city of your planned trip
    - **Trip planning and settling transaction**: Add/ delete events/transactions of one trip
        - linked transaction: link transaction to event
        - User debt: showcase the user debt (if any) to make the expense transparent 
    -  **Analysis**: provide analysis on the expense of one trip
        - Category: analysis of the spending by category
        - Daily Expense: analysis of the spending by day

## Data Collection and Processing
**API Integration**
    - Maps Embed API (Google Map Platform):
        Embed the map of the city into the trip
    - 5-day weather forecast (OpenWeather):
        - Get a 5-day forecast of the weather of the city

**Organic data**
    - Collect data users generate for 
      - User account
      - Trip
      - Event
      - Transaction

## Running the Application
1. **Setup Environment**:
    - Set up a Python virtual environment [Optional]
    - Install required Python packages: 'pip3 install -r requirements.txt'

2. **Starting the App**:
    - you can run the Flask app by
      - 'flask run --debug'
      - 'python run.py'

3. **Using the App**:
    - You can make your account by registering your account
    - Demo accounts are (name: password)
        1. Anna: anna1234
        2. Billy: billy1234
        3. Coffee: coffee1234
        4. Dan: dan1234
        5. Elsa: elsa1234