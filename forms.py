from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length

# Set your classes here.


class RegisterForm(Form):
    name = TextField(
        'Username', validators=[DataRequired(), Length(min=6, max=25)]
    )
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
        EqualTo('password', message='Passwords must match')]
    )
    type = SelectField(
        'Select Type',
        choices=[('sub','Subscriber'),('rev','Reviewer'),('pub','publisher')]
    )


class LoginForm(Form):
    email = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])


class ForgotForm(Form):
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )

class ResetForm(Form):
    password = TextField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
    repeat_password = TextField(
        'Confirm-Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
