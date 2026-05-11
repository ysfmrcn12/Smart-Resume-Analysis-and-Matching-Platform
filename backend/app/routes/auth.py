"""Authentication API endpoints."""
from flask import Blueprint, request, jsonify
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('role') or not data.get('name'):
        return jsonify({'error': 'Missing required fields (email, password, role, name)'}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'A user with that email already exists'}), 400
        
    user = User(
        email=data['email'],
        role=data['role'],
        name=data.get('name'),
        company=data.get('company')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate an existing user."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
        
    return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200