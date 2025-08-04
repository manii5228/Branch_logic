from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField, SelectField,FileField
from wtforms.validators import DataRequired, Email, EqualTo,Optional, Length
from wtforms.fields import EmailField

from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])

    name = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')])
    resume = FileField('Upload Resume', validators=[FileAllowed(['pdf', 'doc', 'docx'])])
    role = SelectField('Registering As', choices=[('student', 'Student'), ('recruiter', 'Recruiter')], validators=[DataRequired()])




class ApplicationStatusUpdateForm(FlaskForm):
    status = SelectField(
        'Update Status',
        choices=[
            ('pending', 'Pending'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('selected', 'Selected')
        ],
        validators=[Optional()]
    )
    remarks = TextAreaField('Remarks (optional)', validators=[Optional()])
    submit = SubmitField('Update')
    


class JobPostForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional()])
    salary_range = StringField('Salary Range', validators=[Optional()])
    skills_required = StringField('Required Skills', validators=[Optional()])
    deadline = StringField('Deadline (YYYY-MM-DD)', validators=[Optional()])    
    submit = SubmitField('Post Job')

class TagForm(FlaskForm):
    name = StringField('Tag Name', validators=[DataRequired()])
    submit = SubmitField('Add Tag')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')
