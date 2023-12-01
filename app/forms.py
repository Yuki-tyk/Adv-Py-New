from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, DateField, SubmitField, SelectMultipleField
from wtforms.validators import Length, EqualTo, Email, DataRequired, NumberRange
from datetime import datetime, timedelta
from wtforms.widgets import TextArea

#flask inherit from flask form class
class RegisterForm(FlaskForm):
    username = StringField(label = 'User name: ', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email address: ', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')
    
class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class ProfileForm(FlaskForm):
    username = StringField('Username', render_kw={'readonly': True})
    email = StringField(label='Email: ', render_kw={'readonly': True})
    userID = StringField(label='userID: ', render_kw={'readonly': True})
    update_password_submit = SubmitField(label='Update Password')
    destroy_account_submit = SubmitField(label='Delete Account')

class UpdatePasswordForm(FlaskForm):
    newpassword1 = PasswordField('New Password', validators=[Length(min=6), DataRequired()])
    newpassword2 = PasswordField('Confirm Password',  validators=[EqualTo('newpassword1', message='Password confirmation does not match'), DataRequired()])
    submit = SubmitField('Update Password')

class DeleteAccountForm(FlaskForm):
    password = PasswordField('Enter Your Password To Delete Account', validators=[Length(min=6), DataRequired()])
    submit = SubmitField('Delete Account')

class EditEventForm(FlaskForm):
    default_time = datetime.now()
    
    eventName = StringField('Event Name')
    linkedTrip = StringField('In which trip this transaction happens?')
    description = StringField('Description')
    startTime = StringField('Start Date & Time (format: YYYY-MM-DD HH:MM)', validators=[DataRequired()], default=default_time.strftime('%Y-%m-%d %H:%M'))
    endTime = StringField('End Date & Time (format: YYYY-MM-DD HH:MM)', validators=[DataRequired()], default=(default_time + timedelta(days=2)).strftime('%Y-%m-%d %H:%M'))

    submit = SubmitField('Save Event')

class EditTransactionForm(FlaskForm):
    default_time = datetime.now()
    default_currency = 'HKD' # ideally change it to the currency of the trip

    transactionName = StringField('Transaction Name')
    linkedTrip = StringField('In which trip this transaction happens?')
    linkedEvent = StringField("")
    #IntegerField('', validators=[NumberRange(min=300000, max=399999)]) # using this becomes a required field somehow
    amount = FloatField('Total Amount', validators=[DataRequired(message='Total amount - please input a positive float value.'), NumberRange(min=0.0, message='Total amount - please input a positive float value.')])
    currency = StringField('Currency', validators=[DataRequired()], default=default_currency)
    transDateTime = StringField('Date & Time (format: YYYY-MM-DD HH:MM)', validators=[DataRequired()], default=default_time.strftime('%Y-%m-%d %H:%M'))

    submit = SubmitField('Save Transaction')

class EditTripForm(FlaskForm):
    tripname = StringField('Trip Name', validators=[DataRequired()])
    location = StringField('Location (City)', validators=[DataRequired()])
    linkedUser = StringField('Who involves in this event?', validators=[DataRequired()])
    startTime = DateField('Start Date of the trip', validators=[DataRequired()])
    endTime = DateField('End Date of the trip', validators=[DataRequired()])
    description = StringField('Description', widget=TextArea())

    submit = SubmitField('Add Trip')