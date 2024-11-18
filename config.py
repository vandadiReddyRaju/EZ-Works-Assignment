# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///file_sharing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-jwt-secret-key'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'your-email@gmail.com'  # Use your email
    MAIL_PASSWORD = 'your-email-password'  # Use your email password
    MAIL_DEFAULT_SENDER = 'your-email@gmail.com'  # Use your email
    UPLOAD_FOLDER = './uploads'
