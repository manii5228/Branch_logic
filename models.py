from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -------------------------------
# Association Table for Job Tags
# -------------------------------
job_tags = db.Table('job_tags',
    db.Column('job_id', db.Integer, db.ForeignKey('job.job_id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

# -------------------------------
# Student Table
# -------------------------------
class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    resume = db.Column(db.String(200), nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    skills = db.Column(db.String(200), nullable=True)

    # Applications relationship
    applications = db.relationship('Application', backref='student', lazy=True)





# -------------------------------
# Category Table
# -------------------------------
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


# -------------------------------
# Tag Table
# -------------------------------
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


# -------------------------------
# Job Table
# -------------------------------
class Job(db.Model):
    job_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    salary_range = db.Column(db.String(50), nullable=True)
    skills_required = db.Column(db.String(200), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_visible = db.Column(db.Boolean, default=True)  
    # Foreign key to Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='jobs')

    # Foreign key to Recruiter

    # Many-to-many relationship with Tags
    tags = db.relationship('Tag', secondary=job_tags, backref=db.backref('jobs', lazy='dynamic'))

    # Applications relationship
    applications = db.relationship('Application', backref='job', lazy=True)


# -------------------------------
# Application Table
# -------------------------------
class Application(db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # e.g., pending, shortlisted, rejected
