from wtforms import Form, BooleanField, PasswordField, StringField, validators

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=2, max=220)])
    email = StringField('Email', [validators.Length(min=6, max=220)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message='Password must match!')])
    confirm = PasswordField('Confirm password')
    accept_tos = BooleanField('I accept the terms of service', [validators.DataRequired()])
    