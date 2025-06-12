from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FileField, validators
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rafa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# Models
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    nationality = db.Column(db.String(50), nullable=False)
    passport = db.Column(db.String(50))
    cin = db.Column(db.String(50))
    service_type = db.Column(db.String(50), nullable=False)
    custom_service = db.Column(db.String(100))
    photo_path = db.Column(db.String(200))
    documents_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_group = db.Column(db.Boolean, default=False)

class GroupProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    documents_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group_profile.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    passport = db.Column(db.String(50))

# Forms
class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[validators.InputRequired()])
    last_name = StringField('Last Name', validators=[validators.InputRequired()])
    phone = StringField('Phone', validators=[validators.InputRequired()])
    email = StringField('Email')
    nationality = StringField('Nationality', validators=[validators.InputRequired()])
    passport = StringField('Passport Number')
    cin = StringField('CIN')
    service_type = SelectField('Service Type', choices=[
        ('visa', 'Visa'),
        ('hotel', 'Hotel'),
        ('billet', 'Billet'),
        ('hajj', 'Hajj'),
        ('omra', 'Omra'),
        ('other', 'Other (Please specify)')
    ], validators=[validators.InputRequired()])
    custom_service = StringField('Custom Service')
    photo = FileField('Profile Photo')
    documents = FileField('Documents')

class GroupForm(FlaskForm):
    group_name = StringField('Group/Organization Name', validators=[validators.InputRequired()])
    group_documents = FileField('Group Documents')

# Routes
@app.route('/')
def index():
    return render_template('index.html', now=datetime.now())

@app.route('/create', methods=['GET', 'POST'])
def create_profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        # Handle file uploads
        photo_filename = None
        if form.photo.data:
            photo_filename = save_file(form.photo.data)
        
        documents_filename = None
        if form.documents.data:
            documents_filename = save_file(form.documents.data)
        
        # Create profile
        profile = Profile(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            email=form.email.data,
            nationality=form.nationality.data,
            passport=form.passport.data,
            cin=form.cin.data,
            service_type=form.service_type.data,
            custom_service=form.custom_service.data if form.service_type.data == 'other' else None,
            photo_path=photo_filename,
            documents_path=documents_filename
        )
        
        db.session.add(profile)
        db.session.commit()
        
        flash('Profile created successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_profile.html', form=form)

@app.route('/group', methods=['GET', 'POST'])
def create_group():
    form = GroupForm()
    
    if form.validate_on_submit():
        # Handle file upload
        documents_filename = None
        if form.group_documents.data:
            documents_filename = save_file(form.group_documents.data)
        
        # Create group
        group = GroupProfile(
            group_name=form.group_name.data,
            documents_path=documents_filename
        )
        
        db.session.add(group)
        db.session.commit()
        
        flash('Group created successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_group.html', form=form)

# Helper functions
def save_file(file):
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)