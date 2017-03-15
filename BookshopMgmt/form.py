from flask.ext.wtf import Form
from wtforms.fields import TextField,SubmitField,PasswordField
from wtforms.validators import Required

class mySignUpForm(Form):
	username = TextField("Username")
	email = TextField("Email")
	password = PasswordField("Password")
	submit = SubmitField("Sign Up")