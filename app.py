# app.py

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message
from bcrypt import hashpw, gensalt, checkpw
from models import db, User, File
from utils import generate_secure_url, validate_secure_url
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)
mail = Mail(app)

# Helper function to send verification email
def send_verification_email(user_email, user_id):
    token = generate_secure_url(user_id)
    verification_link = f"http://127.0.0.1:5000/verify-email/{token}"
    msg = Message("Email Verification", recipients=[user_email])
    msg.body = f"Click here to verify your email: {verification_link}"
    mail.send(msg)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered!"}), 400

    hashed_password = hashpw(data['password'].encode(), gensalt()).decode()
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    # Send verification email
    send_verification_email(new_user.email, new_user.id)

    return jsonify({"message": "Signup successful! Please verify your email."}), 201

@app.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    user_id = validate_secure_url(token)
    if not user_id:
        return jsonify({"message": "The verification link is invalid or expired."}), 400

    user = User.query.get(user_id)
    if user:
        user.is_verified = True
        db.session.commit()
        return jsonify({"message": "Email verified successfully!"}), 200
    return jsonify({"message": "User not found!"}), 404

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and checkpw(data['password'].encode(), user.password.encode()):
        token = create_access_token(identity={'id': user.id, 'is_ops': user.is_ops})
        return jsonify({"access_token": token}), 200
    return jsonify({"message": "Invalid credentials!"}), 401

@app.route('/files', methods=['GET'])
@jwt_required()
def list_files():
    current_user = get_jwt_identity()
    if current_user['is_ops']:
        return jsonify({"message": "Ops user cannot list files!"}), 403

    files = File.query.all()
    return jsonify([{"id": file.id, "filename": file.filename, "uploaded_at": file.uploaded_at} for file in files]), 200

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    if current_user['is_ops']:
        file = request.files['file']
        if file and file.filename.endswith(('pptx', 'docx', 'xlsx')):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            new_file = File(filename=file.filename, user_id=current_user['id'])
            db.session.add(new_file)
            db.session.commit()
            return jsonify({"message": "File uploaded successfully!"}), 201
        return jsonify({"message": "Only pptx, docx, and xlsx files are allowed!"}), 400
    return jsonify({"message": "Only Ops users can upload files!"}), 403

@app.route('/download/<token>', methods=['GET'])
@jwt_required()
def download_file(token):
    current_user = get_jwt_identity()
    file_id = validate_secure_url(token)
    if not file_id:
        return jsonify({"message": "Invalid or expired URL!"}), 403

    file = File.query.get(file_id)
    if not file:
        return jsonify({"message": "File not found!"}), 404

    if current_user['is_ops']:
        return jsonify({"message": "Ops user cannot download files!"}), 403

    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename)

if __name__ == '__main__':
    app.run(debug=True)
