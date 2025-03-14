from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Regexp


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class UploadForm(FlaskForm):
    file = FileField("Upload Image", validators=[
        FileRequired(message="File is required."),
        FileAllowed(['jpg', 'png'], message="Only .jpg and .png files are allowed.")
    ])
    submit = SubmitField("Upload")