# utils.py

from itsdangerous import URLSafeTimedSerializer
from flask import current_app

# Generate a secure URL for email verification
def generate_secure_url(user_id):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user_id, salt='file-upload')

# Validate the secure URL
def validate_secure_url(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        user_id = serializer.loads(token, salt='file-upload', max_age=3600)  # Token expires in 1 hour
        return user_id
    except Exception:
        return None
