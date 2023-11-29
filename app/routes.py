# Internal Import
from app import app ,login_manager
from app.models.toolbox.ID_operation import id_read
from app.models.user import User
from app.models.trip import Trip
from app.models.trip_UserNet import Trip_UserNet
from app.models.event import Event
from app.models.transaction import Transaction
from app import bcrypt
from app.forms import RegisterForm, LoginForm, ProfileForm, UpdatePasswordForm, DeleteAccountForm, EditEventForm, EditTransactionForm, EditTripForm


# External Import
from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request
import json
from datetime import datetime
from app.models.toolbox import api_weather

# data files
global USER_CREDENTIALS
USER_CREDENTIALS = './app/data/users.json'

#read trips.json file
def getTripData():
    with open('app/data/trips.json', 'r') as file:
        trip_data = json.load(file)
    return trip_data

@login_manager.user_loader
def load_user(userID):
    #read user_json file (can optimaize)
    with open(USER_CREDENTIALS, 'r') as f:
        user_data = json.load(f)
    for key, value in user_data.items():
        if value["userID"] == userID:

            return User(value['userID'], 
                value['username'],
                value['email_address'],
                value['password'])
            
@app.route('/')
def index():
    return render_template('pages/homeNonLogin.html')

@app.route('/home')
@login_required
def home_page():
    return render_template('pages/home.html', name=current_user.username)

@app.route('/temp')
def temp_page():
    return render_template('pages/tempLoggedin.html')


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
            
    return render_template('auth/register.html', form=form)

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
        
        # check username match (can optimaize)
        
        for key, value in user_data.items():
            if attempted_username == value["username"]:
                user = user_data[key]
                user_obj = User(user['userID'], user['username'], user['email_address'], user['password'])
                if  user_obj.password_check(attempted_password):
                    login_user(user_obj)
                    flash(f'You are logged in as: {attempted_username}', category='success')
                    login = True
                    return redirect(url_for('home_page'))
            
        flash("Wrong username or password. Please try again.", category='danger')
        
    return render_template('auth/login.html', form=form)

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
    
    return render_template('auth/profile.html', form=form)

@app.route('/updatepw', methods=['GET', 'POST'])
@login_required
def updatepw_page():
    form = UpdatePasswordForm()
    
    if form.validate_on_submit():
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
    return render_template('auth/updatepw.html', form=form)

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
                    return render_template('auth/deleteaccount.html', form=form)
                return redirect(url_for('login_page'))

    return render_template('auth/deleteaccount.html', form=form)

@app.route('/AllTrip')
@login_required
def AllTrip_page():
    trips_data = getTripData()

    user_trip = {}
    for key, value in trips_data.items():
        if current_user.id in [UID for UID in value["accessBy"]]:
            value["startDate"] = datetime.strptime(value['startDate'], '%Y-%m-%d').date()
            value["endDate"] = datetime.strptime(value['endDate'], '%Y-%m-%d').date()
            value["is_past"] = True if value["endDate"] < datetime.now().date() else False
            value["is_present"] = True if value["startDate"] <= datetime.now().date() <= value["endDate"] else False
            value["is_future"] = True if value["startDate"] > datetime.now().date() else False
            user_trip[key] = value

    
    return render_template('pages/AllTrip.html', user_trip = user_trip)

# plus button at bottom left
@app.route('/trip/<trip_ID>')
@login_required
def trip_page(trip_ID):
    current_trip = Trip.read(trip_ID)
    if current_trip == -1:
        flash("Trip not found. You are returned to the trips page.", category="danger")
        return redirect(url_for('AllTrip_page'))
    activities = current_trip.view_linked()

    #get weather
    weather = api_weather.weather(current_trip.location)

    #get now times
    nowTime = datetime.now().date()
    nowTime = nowTime.strftime("%Y-%m-%d")

    weather_json = {nowTime:weather.get_current_weather()}
    weather_json.update(weather.get_forecast_weather())

    # get the net amount of all user in the current trip
    linkedUser = current_trip.accessBy
    
    ### not cater for the case where a deleted user is still in the trip
    users_net = []
    name_list = []
    for user in linkedUser:
        try:
            temp = User.read(user).username
            if temp == -1:
                continue
        except:
            temp = "[Deleted Account]"
        users_net.append([temp, Trip_UserNet.read(user, trip_ID).net])

    print(current_trip)
    
    

    # print('-------------------------------------------')
    # print(users_net)
    # print('-------------------------------------------')
    return render_template('pages/trip.html', trip_attributes = current_trip, weather = weather_json, activities = activities, users_net = users_net)

@app.route('/templist/<trip_ID>')
@login_required
def templist(trip_ID):
    active_trip = Trip.read(trip_ID)
    activities = active_trip.view_linked()
    return render_template('pages/templist.html',trip_ID=trip_ID, activities=activities)

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
            return redirect(url_for('AllTrip_page'))

        if not(location.lower() in [string.lower() for string in city_list]):
            flash("Location invalid. Note that the location should be a city. Please try again.", category="danger")
        
        if not(startTime<=endTime):
            flash("Start date should be earlier than end date. Please try again.", category="danger")

    return render_template('edit/e_trip.html', form=form)

@app.route('/editEvent', methods=['GET', 'POST'])
@login_required
def editEvent_page():
    # create from instance
    form = EditEventForm()
    
    #get triggered when submit button is clicked, and check the validation
    if form.validate_on_submit():
        name = form.eventName.data
        if name == "":
            name = "Event"
        linkedUser = [UID.strip() for UID in form.linkedUser.data.split(",")]
        linkedTrip = str(form.linkedTrip.data)
        description = form.description.data
        startTime = form.startTime.data
        endTime = form.endTime.data
        try:
            newEvent = Event.create(linkedUser, linkedTrip, name, description, startTime, endTime)

            # handle no such user error
            if newEvent == -1:
                flash("UserID(s) not found. Please try again.", category="danger")
                print('-------------------------------------------')
                print("UserID(s) not found. Event creation failed.")
                print('-------------------------------------------')
            
            # handle no such trip error
            if newEvent == -2:
                flash("TripID not found. Please try again.", category="danger")
                print('-------------------------------------------')
                print("TripID not found. Event creation failed.")
                print('-------------------------------------------')
            
            if newEvent in [-1, -2]:
                return render_template('edit/e_event.html', form=form)
        except:
            flash("Event creation failed.", category="danger")
            print('-------------------------------------------')
            print("Event creation failed")
            print('-------------------------------------------')
            return render_template('edit/e_event.html', form=form)
        
        # new event created successfully
        flash("Event created successfully. Enjoy your trip!", category="success")
        print('-------------------------------------------')
        print("Event creation successful. (ID: %s)" %newEvent.ID)
        print('-------------------------------------------')
        return redirect(url_for('trip_page', trip_ID=newEvent.linkedTrip))
    
    # If there are not errors from the validations
    if form.errors != {}:
        for error_msg in form.errors.values():
            flash(error_msg, category="danger")
            
    return render_template('edit/e_event.html', form=form)

@app.route('/editTransaction', methods=['GET', 'POST'])
@login_required
def editTransaction():
    # create from instance
    form = EditTransactionForm()
    
    #get triggered when submit button is clicked, and check the validation
    if form.validate_on_submit():
        name = form.transactionName.data
        if name == "":
            name = "Expense"
        amount = form.amount.data
        # try:
        #     amount = float(form.amount.data)
        # except:
        #     flash("Amount must be a number (eg 100). Please try again.", category="danger")
        #     return render_template('edit/e_transaction.html', form=form)
        currency = form.currency.data
        linkedTrip = str(form.linkedTrip.data)
        linkedEvent = form.linkedEvent.data
        paidUsers = [UID.strip() for UID in form.paidUser.data.split(",")]
        receivedUsers = [UID.strip() for UID in form.receivedUser.data.split(",")]
        transDateTime = form.transDateTime.data

        # for now, we assume the amount paid and the amount received are evenly distributed among the users
        paidPerUser = amount / len(paidUsers)
        receivedPerUser = amount / len(receivedUsers) 

        # create a dictionary of the users involved in the transaction
        linkedUser = {}
        for user in paidUsers:
            if user in receivedUsers:
                linkedUser[user] = {"paid": paidPerUser, "received": receivedPerUser}
                receivedUsers.remove(user)
            else:
                linkedUser[user] = {"paid": paidPerUser, "received": 0}
        for user in receivedUsers:
            linkedUser[user] = {"paid": 0, "received": receivedPerUser}
        
        # handle debt settlement and category
        if "debtSettlement" in request.form:
            debtSettlement = True
            category = None
        else:
            debtSettlement = False
            category = Transaction.getCategoryInt(request.form['category'])

        try:
            if linkedEvent == "":
                newTransaction = Transaction.create(linkedUser, linkedTrip, name, category, transDateTime, currency, debtSettlement)
            else:
                newTransaction = Transaction.create(linkedUser, linkedTrip, name, category, transDateTime, currency, debtSettlement, linkedEvent)
            print(newTransaction)
            # handle no such user error
            if newTransaction == -1:
                flash("UserID(s) not found. Please try again.", category="danger")
                print('-------------------------------------------')
                print("UserID(s) not found. Transaction creation failed.")
                print('-------------------------------------------')

            # handle no such trip error
            if newTransaction == -2:
                flash("TripID not found. Please try again.", category="danger")
                print('-------------------------------------------')
                print("TripID not found. Transaction creation failed.")
                print('-------------------------------------------')
            
            if newTransaction in [-1, -2]:
                return render_template('edit/e_transaction.html', form=form)
        except:
            flash("Transaction creation failed.", category="danger")
            print('-------------------------------------------')
            print("Transaction creation failed")
            print("linkedUser: %s" %linkedUser)
            print('-------------------------------------------')
            return render_template('edit/e_transaction.html', form=form)
        
        # new transaction created successfully
        print(newTransaction)
        flash("Transaction created successfully. Enjoy your trip!", category="success")
        print('-------------------------------------------')
        print("Transaction creation successful. (ID: %s)" %newTransaction.ID)
        print('-------------------------------------------')
        return redirect(url_for('trip_page', trip_ID=newTransaction.linkedTrip))
    
    # If there are not errors from the validations, email format 
    if form.errors != {}:
        for error_msg in form.errors.values():
            flash(error_msg, category="danger")
            
    return render_template('edit/e_transaction.html', form=form)

# get the tripID and tripName of all trips that the user has access to
@app.route('/get_trip_data', methods=['GET'])
def get_trip_data_route():
    trips_data = getTripData()
    print("trips_data function")

    user_trip = {}
    for key, value in trips_data.items():
        if current_user.id in [UID for UID in value["accessBy"]]:
            user_trip[key] = value["tripID"]
            user_trip[value["tripID"]] = value["tripName"]
    print(user_trip)
    # return jsonify(user_trip)