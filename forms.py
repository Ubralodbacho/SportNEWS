from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import StringField, SubmitField, TextAreaField, PasswordField, SelectField
from wtforms.validators import DataRequired, equal_to, Optional

class NewsForm(FlaskForm):
    name = StringField("სახელი", validators=[DataRequired()])
    img = FileField("სურათი", validators=[FileRequired(),FileAllowed(["jpg", "png", "jpeg"], "მხარდასაჭირია მხოლოდ სურათის ფორმატები: jpg, png, jpeg"), Optional()])
    descrip = TextAreaField("აღწერა", validators=[DataRequired()])   
    category = SelectField("კატეგორია", choices=[('football', 'ფეხბურთი'), ('basketball', 'კალათბურთი'), ('tennis', 'ჩოგბურთი'), ('other', 'სხვა')], validators=[DataRequired()])
    
    submit = SubmitField("ღილაკი")


class RegisterForm(FlaskForm):
    username = StringField("იუზერნეიმი", validators=[DataRequired()])
    password = PasswordField("პაროლი", validators= [DataRequired()])
    repeat_password = PasswordField("გაიმეორეთ პაროლი", validators = [equal_to("password")])
    register = SubmitField("რეგისტრაცია")

class LoginForm(FlaskForm):
    username = StringField("იუზერნეიმი", validators=[DataRequired()])
    password = PasswordField("პაროლი", validators= [DataRequired()])
    login = SubmitField("ავტორიზაცია")

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
