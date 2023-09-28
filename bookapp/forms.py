from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired , FileAllowed
from wtforms import StringField,SubmitField,TextAreaField,PasswordField,SubmitField
from wtforms.validators import Email,DataRequired,EqualTo,Length

class RegForm(FlaskForm):
    fullname= StringField("FirstName",validators=[DataRequired(message="The first name is a must")])   
    email= StringField("Email",validators=[Email(message="Invalid Email"),DataRequired(message='Email must be suplied')])
    pwd= PasswordField("Enter Password",validators=[DataRequired()])
    confpwd= PasswordField("Confirm Password",validators=[EqualTo('pwd',message="brod")])    
    btnsubmit=SubmitField("Register!")


class  DpForm(FlaskForm) :
    dp = FileField("upload a Profile picture",validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'])])
    btnupload = SubmitField("upload picture")


class ProfileForm(FlaskForm):
    fullname= StringField("FirstName",validators=[DataRequired(message="The first name is a must")])   
    btnsubmit=SubmitField("update profile!")


class ContactForm(FlaskForm):
    email= StringField("Email",validators=[DataRequired(message="Enter a valid email")])   
    btnsubmit=SubmitField("Update profile")


class DonateForm(FlaskForm):
    fullname= StringField("FirstName",validators=[DataRequired(message="The first name is a must")])   
    email= StringField("Email",validators=[Email(message="Invalid Email"),DataRequired(message='Email must be suplied')])
    amt= StringField("Amt",validators=[Email(message="Invalid Email"),DataRequired(message='Email must be suplied')])
    btnsubmit=SubmitField("continue")