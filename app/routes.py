# Internal Import
from app import app ,login_manager
from app.models.toolbox.ID_operation import id_read
from app.models.user import User
from app.models.trip import Trip
from app.models.trip_UserNet import Trip_UserNet
from app.models.event import Event
from app.models.transaction import Transaction
from app.models.toolbox import api_weather
from app.models.toolbox.api_weather import Weather
from app import bcrypt
from app.forms import RegisterForm, LoginForm, ProfileForm, UpdatePasswordForm, DeleteAccountForm, EditEventForm, EditTransactionForm, EditTripForm


# External Import
from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, jsonify
import json
from datetime import datetime

# data files
global USER_CREDENTIALS
USER_CREDENTIALS = './app/data/users.json'

@login_manager.user_loader
def load_user(userID):
    #read user_json file (can optimize)
    with open(USER_CREDENTIALS, 'r') as f:
        user_data = json.load(f)
    for key, value in user_data.items():
        try:
            if value["userID"] == userID:
                return User(value['userID'], 
                    value['username'],
                    value['email_address'],
                    value['password'])
        except:
            pass # do nothing if the user is deleted
            
@app.route('/')
def index():
        if current_user.is_authenticated:
            return redirect(url_for('home_page'))
        else:
            return render_template('pages/homeNonLogin.html', data={})

@app.route('/home')
@login_required
def home_page():
    return render_template('pages/home.html', name=current_user.username, data = {})

@app.route('/temp')
def temp_page():
    return render_template('pages/tempLoggedin.html', data = {})


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    # create from instance
    form = RegisterForm()
    
    #get triggered when submit button is clicked, and check the validation
    if form.validate_on_submit():
        username=form.username.data
        #read user_json file
        with open(USER_CREDENTIALS, 'r') as f:
            user_data = json.load(f)
        
        #if same user name, alert (can optimaize)
        for key, value in user_data.items():
            if(value["username"] == username):
                flash("Sorry. Username already exists. Please try again.", category="danger")
                return render_template('auth/register.html', form=form)
            
        user_dict = dict(username=form.username.data, 
                         email_address=form.email_address.data, 
                         password=bcrypt.generate_password_hash(form.password1.data).decode('utf-8'))
        
        temp = User.create(**user_dict)
        user_dict['userID'] = temp.id
        user_data[temp.id] = user_dict

        return redirect(url_for('home_page'))
    
    # If there are not errors from the validations, email format 
    if form.errors != {}:
        for error_msg in form.errors.values():
            flash(error_msg, category="danger")
            
    return render_template('auth/register.html', form=form, data = {})

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    
    # create from instance
    form = LoginForm()
    
    #read user_json file
    with open(USER_CREDENTIALS, 'r') as f:
        user_data = json.load(f)
        
    if form.validate_on_submit():
        attempted_username=form.username.data
        attempted_password=form.password.data
        
        # check username match (can optimize)
        for key, value in user_data.items():
            try:
                if attempted_username == value["username"]:
                    user = user_data[key]
                    user_obj = User(user['userID'], user['username'], user['email_address'], user['password'])
                    if  user_obj.password_check(attempted_password):
                        login_user(user_obj)
                        flash(f'You are logged in as: {attempted_username}', category='success')
                        login = True
                        return redirect(url_for('home_page'))
            except:
                pass # do nothing if the user is deleted
            
        flash("Wrong username or password. Please try again.", category='danger')
        
    return render_template('auth/login.html', form=form, data = {})

@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash("You are logged out.", category='info')
    return redirect(url_for('login_page'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    form = ProfileForm()

    form.username.data = current_user.username
    form.email.data = current_user.email
    form.userID.data = current_user.id
    
    if form.update_password_submit.data:
        return redirect(url_for('updatepw_page'))
    
    if form.destroy_account_submit.data:
        return redirect(url_for('deleteaccount_page'))
    
    return render_template('auth/profile.html', form=form, data = {})

@app.route('/updatepw', methods=['GET', 'POST'])
@login_required
def updatepw_page():
    form = UpdatePasswordForm()
    
    if form.validate_on_submit():
        # check if the current password is correct
        if not bcrypt.check_password_hash(current_user.password, form.currentPassword.data):
            flash('Current password is incorrect. Please try again.', category="danger")
            return render_template('auth/updatepw.html', form=form, data = {})

        with open(USER_CREDENTIALS, 'r') as f:
            user_data = json.load(f)

        for key,value in user_data.items():
            if(value["username"] == current_user.username):
                value['password'] = bcrypt.generate_password_hash(form.newpassword1.data).decode('utf-8')
                with open(USER_CREDENTIALS, 'w') as f:
                    json.dump(user_data, f, indent=4)
                flash(f'Your password is changed', category='success')
                return redirect(url_for('profile_page'))
    
    # If there are not errors from the validations, email format 
    if form.errors != {}:
        for error_msg in form.errors.values():
            flash(error_msg, category="danger")
    return render_template('auth/updatepw.html', form=form, data = {})

@app.route('/deleteaccount', methods=['GET', 'POST'])
@login_required
def deleteaccount_page():
    form = DeleteAccountForm()

    if form.validate_on_submit():
        with open(USER_CREDENTIALS, 'r') as f:
            user_data = json.load(f)

        for key,value in user_data.items():
            if (value["username"] == current_user.username):
                if(bcrypt.check_password_hash(current_user.password, form.password.data)):
                    del user_data[current_user.id]

                    User.delete(current_user.id)
                        
                    flash("You deleted your account", category='info')
                    logout_user()
                else:
                    flash('password error', category="danger")
                    return render_template('auth/deleteaccount.html', form=form, data = {})
                return redirect(url_for('login_page'))

    return render_template('auth/deleteaccount.html', form=form, data = {})

@app.route('/AllTrips')
@login_required
def AllTrips_page():
    trips_data = Trip.read_all()

    user_trip = {}
    for key, value in trips_data.items():
        if current_user.id in [UID for UID in value["accessBy"]]:
            value["startDate"] = datetime.strptime(value['startDate'], '%Y-%m-%d').date()
            value["endDate"] = datetime.strptime(value['endDate'], '%Y-%m-%d').date()
            value["is_past"] = True if value["endDate"] < datetime.now().date() else False
            value["is_present"] = True if value["startDate"] <= datetime.now().date() <= value["endDate"] else False
            value["is_future"] = True if value["startDate"] > datetime.now().date() else False
            user_trip[key] = value
    
    return render_template('pages/AllTrips.html', user_trip = user_trip, data = {})

# plus button at bottom left
@app.route('/trip/<trip_ID>')
@login_required
def trip_page(trip_ID):
    current_trip = Trip.read(trip_ID)
    if (current_trip == -1) or (current_user.id not in current_trip.accessBy):
        flash("Trip not found. You are returned to the trips page.", category="danger")
        return redirect(url_for('AllTrips_page'))
    activities = current_trip.view_linked()
    activities = current_trip.view_linked()

    linkedTransactions = {key: value for key, value in activities.items() if value['type'] == 'Transaction'}

    # print("-------------------------------------------")
    # print("linkedTransactions: ", linkedTransactions)
    # print("-------------------------------------------")

    # create an instance of Weather
    weatherData = Weather(current_trip.location)

    # get the current weather and forecast weather
    # weatherDict = {nowTime:weatherData.get_current_weather()}
    weatherDict = weatherData.get_current_weather()
    weatherDict.update(weatherData.get_forecast_weather())

    plot_url = Weather.plot_forecast(weatherDict, current_trip.location)

    user_debt_graph = current_user.user_debt(trip_ID)
    # get the net amount of all user in the current trip
    linkedUser = current_trip.accessBy
    
    users_net = []
    for user in linkedUser:
        try:
            temp = User.read(user).username
            if temp == -1:
                continue
        except:
            temp = "[Deleted Account]"
        users_net.append([temp, Trip_UserNet.read(user, trip_ID).net])

    users_net.reverse()
    return render_template('pages/trip.html', trip_attributes = current_trip, weather = weatherDict, activities = activities, users_net = users_net, plot_url = plot_url, user_debt_graph=user_debt_graph, data = {})

@app.route('/debt_settle', method= ['POST'])
def debt_settle(tripID):
    return





@app.route('/analysis')
def analysis():
    # get trip info
    tripID = request.args.get('tripID')
    trip = Trip.read(tripID)
    user_debt = current_user.user_debt(tripID)
    daily_expense = trip.plot_daily_expense()
    plot_spending = trip.plot_spending()
    return render_template('pages/analysis.html', user_debt = user_debt, daily_expense = daily_expense, plot_spending = plot_spending, data={})


@app.route('/editTrip', methods=['GET', 'POST'])
@login_required
def editTrip_page():
    form = EditTripForm()
    if form.validate_on_submit():
        tripname = form.tripname.data
        location = form.location.data.title()
        linkedUser = [str(UID.strip()) for UID in form.linkedUser.data.split(",")]
        description = form.description.data
        startTime =  form.startTime.data.strftime('%Y-%m-%d')
        endTime = form.endTime.data.strftime('%Y-%m-%d')
        description = form.description.data

        with open('app/data/cities.json') as file:
            cities_data = json.load(file)

        city_list = cities_data['cities']
        if location.lower() in [string.lower() for string in city_list] and startTime<=endTime:   
            newTrip = Trip.create(str(current_user.id), tripname, startTime, endTime, description, location, linkedUser)
            return redirect(url_for('AllTrips_page'))

        if not(location.lower() in [string.lower() for string in city_list]):
            flash("Location invalid. Note that the location should be a city. Please try again.", category="danger")
        
        if not(startTime<=endTime):
            flash("Start date should be earlier than end date. Please try again.", category="danger")

    return render_template('edit/e_trip.html', form=form, data = {})

@app.route('/editEvent', methods=['GET', 'POST'])
@login_required
def editEvent_page():
    # get trip info
    tripID = request.args.get('tripID')
    trip = Trip.read(tripID)
    
    if (trip == -1) or (current_user.id not in trip.accessBy):
        flash("Trip not found. You are returned to the trips page.", category="danger")
        return redirect(url_for('AllTrips_page'))

    # get the user names in the trip
    tripUsers = trip.accessBy # list of user IDs that are in the trip
    tripUserNames = User.userIDsToUserNames(tripUsers) # list of user names that are in the trip

    # create from instance
    form = EditEventForm()
    
    #get triggered when submit button is clicked, and check the validation
    if form.validate_on_submit():
        name = form.eventName.data
        if name == "":
            name = "Event"
        
        # get linkedUserNames
        linkedUserNames = request.form.getlist('linkedUserNames')

        # check if linkedUserName is empty
        if len(linkedUserNames) == 0:
            flash("Please select at least one linked tripper for this event.", category="danger")
            return render_template('edit/e_event.html', form = form, tripName = trip.name, tripUserNames = tripUserNames, data = {})

        # convert linkedUserNames to linkedUsers (IDs)
        linkedUsers = User.userNamesToUserIDs(linkedUserNames)
        
        linkedTrip = str(tripID)
        description = form.description.data
        startTime = form.startTime.data
        endTime = form.endTime.data

        # check if startTime and endTime are valid
        if checkActivityDate(startTime) == "Invalid Date":
            flash("Invalid start date. Please try again.", category="danger")
            return render_template('edit/e_event.html', form = form, tripName = trip.name, tripUserNames = tripUserNames, data = {})
        if checkActivityDate(endTime) == "Invalid Date":
            flash("Invalid end date. Please try again.", category="danger")
            return render_template('edit/e_event.html', form = form, tripName = trip.name, tripUserNames = tripUserNames, data = {})
        if startTime > endTime:
            flash("Start date should be earlier than end date. Please try again.", category="danger")
            return render_template('edit/e_event.html', form = form, tripName = trip.name, tripUserNames = tripUserNames, data = {})

        try:
            newEvent = Event.create(linkedUsers, linkedTrip, name, description, startTime, endTime)

            # # handle no such user error
            # if newEvent == -1:
            #     flash("UserID(s) not found. Please try again.", category="danger")
            #     print('-------------------------------------------')
            #     print("UserID(s) not found. Event creation failed.")
            #     print('-------------------------------------------')
            
            # # handle no such trip error
            # if newEvent == -2:
            #     flash("TripID not found. Please try again.", category="danger")
            #     print('-------------------------------------------')
            #     print("TripID not found. Event creation failed.")
            #     print('-------------------------------------------')
            
            # if newEvent in [-1, -2]:
            #     return render_template('edit/e_event.html', form = form, tripName = trip.name, tripUserNames = tripUserNames, data = {})
        except:
            flash("Event creation failed.", category="danger")
            print('-------------------------------------------')
            print("Event creation failed")
            print('-------------------------------------------')
            return render_template('edit/e_event.html', form=form, tripName = trip.name, tripUserNames = tripUserNames, data = {})
        
        # new event created successfully
        flash("Event created successfully. Enjoy your trip!", category="success")
        print('-------------------------------------------')
        print("Event creation successful. (ID: %s)" %newEvent.ID)
        print('-------------------------------------------')
        return redirect(url_for('trip_page', trip_ID = tripID , data = {}))
    
    # If there are not errors from the validations
    if form.errors != {}:
        for error_msg in form.errors.values():
            flash(error_msg, category="danger")
            
    return render_template('edit/e_event.html', form = form, tripName = trip.name, tripUserNames = tripUserNames, data = {})

@app.route('/editTransaction', methods=['GET', 'POST'])
@login_required
def editTransaction_page():
    # get trip info
    tripID = request.args.get('tripID')
    trip = Trip.read(tripID)
    
    if (trip == -1) or (current_user.id not in trip.accessBy):
        flash("Trip not found. You are returned to the trips page.", category="danger")
        return redirect(url_for('AllTrips_page'))
    
    # get the user names in the trip
    tripUsers = trip.accessBy # list of user IDs that are in the trip
    tripUserNames = User.userIDsToUserNames(tripUsers) # list of user names that are in the trip

    # get the event names in the trip
    tripEvents = trip.linkedEvent # list of event IDs that are in the trip
    tripEventNames = Event.eventIDsToEventNames(tripEvents) # list of event names that are in the trip
    
    # create from instance
    form = EditTransactionForm()
    
    # get triggered when submit button is clicked, and check the validation
    if form.validate_on_submit():
        name = form.transactionName.data
        if name == "":
            name = "Expense"
        amount = form.amount.data
        currency = form.currency.data
        linkedTrip = str(tripID)

        # get linkedEvent
        linkedEventName = request.form['linkedEvent'].split(" (")[0]

        # convert linkedEventName to linkedEvent (IDs)
        linkedEvent = Event.eventNameToEventIDs(linkedEventName)

        # get linkedUsers
        # get paidUserNames and receivedUserNames
        paidUserNames = request.form.getlist('paidUserNames')
        receivedUserNames = request.form.getlist('receivedUserNames')

        # check if paidUserNames is empty
        if len(paidUserNames) == 0:
            flash("Please select at least one paid tripper.", category="danger")
            return render_template('edit/e_transaction.html', form = form, tripName = trip.name, eventNames = tripEventNames, tripUserNames = tripUserNames, data = {})
        # check if receivedUserNames is empty
        if len(receivedUserNames) == 0:
            flash("Please select at least one received tripper.", category="danger")
            return render_template('edit/e_transaction.html', form = form, tripName = trip.name, eventNames = tripEventNames, tripUserNames = tripUserNames, data = {})
        
        # convert paidUserNames to paidUser (IDs)
        paidUsers = User.userNamesToUserIDs(paidUserNames)
        # convert paidUserNames to paidUser (IDs)
        receivedUsers = User.userNamesToUserIDs(receivedUserNames)

        transDateTime = form.transDateTime.data

        # check if transDateTime are valid
        if checkActivityDate(transDateTime) == "Invalid Date":
            flash("Invalid transaction time. Please try again.", category="danger")
            return render_template('edit/e_transaction.html', form = form, tripName = trip.name, eventNames = tripEventNames, tripUserNames = tripUserNames, data = {})


        # for now, we assume the amount paid and the amount received are evenly distributed among the users
        paidPerUser = amount / len(paidUsers)
        receivedPerUser = amount / len(receivedUsers) 

        # create a dictionary of the users involved in the transaction
        linkedUsers = {}
        for user in paidUsers:
            if user in receivedUsers:
                linkedUsers[user] = {"paid": paidPerUser, "received": receivedPerUser}
                receivedUsers.remove(user)
            else:
                linkedUsers[user] = {"paid": paidPerUser, "received": 0}
        for user in receivedUsers:
            linkedUsers[user] = {"paid": 0, "received": receivedPerUser}
        
        # handle debt settlement and category
        if "debtSettlement" in request.form:
            debtSettlement = True
            category = None
        else:
            debtSettlement = False
            category = Transaction.getCategoryInt(request.form['category'])

        try:
            if linkedEvent == "":
                newTransaction = Transaction.create(linkedUsers, linkedTrip, name, category, transDateTime, currency, debtSettlement)
            else:
                newTransaction = Transaction.create(linkedUsers, linkedTrip, name, category, transDateTime, currency, debtSettlement, linkedEvent)
            # # handle no such user error
            # if newTransaction == -1:
            #     flash("UserID(s) not found. Please try again.", category="danger")
            #     print('-------------------------------------------')
            #     print("UserID(s) not found. Transaction creation failed.")
            #     print('-------------------------------------------')

            # # handle no such trip error
            # if newTransaction == -2:
            #     flash("TripID not found. Please try again.", category="danger")
            #     print('-------------------------------------------')
            #     print("TripID not found. Transaction creation failed.")
            #     print('-------------------------------------------')
            
            # if newTransaction in [-1, -2]:
            #     return render_template('edit/e_transaction.html', form = form, tripName = trip.name, tripUserNames = tripUserNames, data = {})
        except:
            flash("Transaction creation failed. Please try again.", category="danger")
            print('-------------------------------------------')
            print("Transaction creation failed")
            print("linkedUser: %s" %linkedUsers)
            print('-------------------------------------------')
            return render_template('edit/e_transaction.html', form = form, tripName = trip.name, eventNames = tripEventNames, tripUserNames = tripUserNames, data = {})
        
        # new transaction created successfully
        print(newTransaction)
        flash("Transaction created successfully. Enjoy your trip!", category="success")
        print('-------------------------------------------')
        print("Transaction creation successful. (ID: %s)" %newTransaction.ID)
        print('-------------------------------------------')
        return redirect(url_for('trip_page', trip_ID = tripID, data = {}))
    
    # If there are not errors from the validations, email format 
    if form.errors != {}:
        for error_msg in form.errors.values():
            flash(error_msg, category="danger")
            
    return render_template('edit/e_transaction.html', form = form, tripName = trip.name, eventNames = tripEventNames, tripUserNames = tripUserNames, data = {})

# get the tripID and tripName of all trips that the user has access to
@app.route('/get_trip_data', methods=['GET'])
def get_trip_data_route():
    trips_data = Trip.read_all()
    user_trip = {}
    for key, value in trips_data.items():
        if current_user.id in [UID for UID in value["accessBy"]]:
            user_trip[key] = value["tripID"]
            user_trip[value["tripID"]] = value["name"]
    return jsonify(user_trip)

@app.route('/edit_eventtrans', methods=['POST'])
def edit_eventtrans():
    tripName = request.form.get('tripName')
    tripID = Trip.getTripIDbyName(tripName)
    return jsonify(tripID=tripID)

@app.route('/delete/event/<eventID>', methods=['DELETE'])
def delete_event(eventID):
    if Event.delete(eventID):
        return jsonify({'message': f'Event {eventID} deleted successfully'})
    else:
        return jsonify({'message': f'Event {eventID} not Found'})

@app.route('/delete/transaction/<transactionID>', methods=['DELETE'])
def delete_transaction(transactionID):
    if Transaction.delete(transactionID):
        return jsonify({'message': f'Transaction {transactionID} deleted successfully'})
    else:
        return jsonify({'message': f'Transaction {transactionID} not Found'})

@app.route('/delete/trip/<tripID>', methods=['DELETE'])
def delete_trip(tripID):
    if Trip.delete(tripID):
        return jsonify({'message': f'Trip {tripID} deleted successfully'})
    else:
        return jsonify({'message': f'Trip {tripID} not Found'})

def checkActivityDate(activityTime: str):
    try:
        return datetime.strptime(activityTime, '%Y-%m-%d %H:%M')
    except:
        return "Invalid Date"
