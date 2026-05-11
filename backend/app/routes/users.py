"""User profile and CV management API endpoints."""
import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_file
from app import db
from app.models import User, UserCV
from app.nlp.resume_parser import ResumeParser

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>/profile', methods=['GET', 'PUT'])
def profile(user_id):
    """Get or update user profile."""
    user = User.query.get_or_404(user_id)
    if request.method == 'GET':
        return jsonify(user.to_dict())
    
    data = request.get_json()
    if 'name' in data:
        user.name = data['name']
    if 'company' in data:
        user.company = data['company']
    
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': user.to_dict()})

@users_bp.route('/<int:user_id>/cvs', methods=['GET', 'POST'])
def manage_cvs(user_id):
    """List or upload user CVs."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return jsonify([cv.to_dict() for cv in user.cvs])
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not ResumeParser.is_supported(file.filename):
        return jsonify({'error': 'Unsupported format. Use PDF, DOCX, or TXT.'}), 400
        
    upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'user_cvs')
    os.makedirs(upload_folder, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1].lower()
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_folder, safe_filename)
    
    file.save(filepath)
    
    cv = UserCV(user_id=user_id, filename=file.filename, filepath=filepath)
    db.session.add(cv)
    db.session.commit()
    
    return jsonify({'message': 'CV uploaded successfully', 'cv': cv.to_dict()}), 201

@users_bp.route('/<int:user_id>/cvs/<int:cv_id>', methods=['GET'])
def get_cv(user_id, cv_id):
    """Download or view a saved CV."""
    cv = UserCV.query.filter_by(id=cv_id, user_id=user_id).first_or_404()
    if os.path.exists(cv.filepath):
        return send_file(
            os.path.abspath(cv.filepath),
            as_attachment=False,
            download_name=cv.filename
        )
    return jsonify({'error': 'File not found on server.'}), 404

@users_bp.route('/<int:user_id>/cvs/<int:cv_id>', methods=['DELETE'])
def delete_cv(user_id, cv_id):
    """Delete a saved CV."""
    cv = UserCV.query.filter_by(id=cv_id, user_id=user_id).first_or_404()
    if os.path.exists(cv.filepath):
        try:
            os.remove(cv.filepath)
        except OSError:
            pass
    db.session.delete(cv)
    db.session.commit()
    return '', 204