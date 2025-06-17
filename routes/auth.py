from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token,
)
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['email', 'password', 'first_name', 'last_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone', ''),
        is_admin=data.get('is_admin', False)
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # Исправление: используем строковый идентификатор
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_admin': user.is_admin
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Исправление: используем строковый идентификатор
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_admin': user.is_admin
    })

    return response, 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        logger.info(f"Requested profile for user_id: {user_id}")

        user = User.query.get(user_id)

        if not user:
            logger.warning(f"User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat()
        }), 200

    except Exception as e:
        logger.exception("Error in profile endpoint")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    allowed_fields = ['first_name', 'last_name', 'phone']
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat()
        }
    }), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 404

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(email, salt='password-reset')

    try:
        reset_url = f"{request.host_url}reset-password/{token}"

        # В реальном приложении здесь должна быть отправка письма
        print(f"Password reset link: {reset_url}")

        return jsonify({
            'message': 'Reset instructions sent',
            'reset_token': token  # Для демо-режима
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not password or not confirm_password:
        return jsonify({'error': 'Password and confirmation are required'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        email = serializer.loads(
            token,
            salt='password-reset',
            max_age=3600  # 1 hour expiration
        )
    except:
        return jsonify({'error': 'Invalid or expired token'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.set_password(password)
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'}), 200

@auth_bp.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    return jsonify({'valid': True}), 200