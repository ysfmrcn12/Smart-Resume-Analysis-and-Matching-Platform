"""Job posting CRUD API endpoints."""
from flask import Blueprint, request, jsonify

from app import db
from app.models import JobPosting, User
from app.nlp.ner_extractor import NERExtractor

jobs_bp = Blueprint('jobs', __name__)
ner_extractor = NERExtractor()

TITLE_MAX_LENGTH = 200
COMPANY_MAX_LENGTH = 200
LOCATION_MAX_LENGTH = 200


def _truncate_str(value, max_len: int) -> str:
    """Truncate incoming strings to DB column limits to avoid 500s."""
    if value is None:
        return ""
    s = str(value).strip()
    if len(s) <= max_len:
        return s
    return s[:max_len]


@jobs_bp.route('', methods=['GET'])
def list_jobs():
    """List all job postings."""
    jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).all()
    return jsonify([j.to_dict() for j in jobs])


@jobs_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get a single job posting by ID."""
    job = JobPosting.query.get_or_404(job_id)
    return jsonify(job.to_dict())


@jobs_bp.route('', methods=['POST'])
def create_job():
    """Create a new job posting."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required to create a job'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role != 'hr':
        return jsonify({'error': 'Only HR users can create jobs'}), 403

    if not data.get('title') or not data.get('description'):
        return jsonify({'error': 'Title and description are required fields'}), 400

    new_job = JobPosting(
        title=data['title'],
        description=data['description'],
        requirements=data.get('requirements', []),
        company=user.company,  # Automatically set company from HR user
        location=data.get('location'),
        user_id=user.id
    )
    db.session.add(new_job)
    db.session.commit()

    return jsonify(new_job.to_dict()), 201


@jobs_bp.route('/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Update a job posting."""
    job = JobPosting.query.get_or_404(job_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'title' in data:
        job.title = _truncate_str(data['title'], TITLE_MAX_LENGTH)
    if 'description' in data:
        job.description = data['description']
    if 'requirements' in data:
        job.requirements = data['requirements'] or []
    if 'company' in data:
        job.company = _truncate_str(data['company'], COMPANY_MAX_LENGTH)
    if 'location' in data:
        job.location = _truncate_str(data['location'], LOCATION_MAX_LENGTH)

    db.session.commit()
    return jsonify(job.to_dict())


@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job posting."""
    job = JobPosting.query.get_or_404(job_id)
    user_id = request.args.get('user_id')
    if not user_id or str(job.user_id) != str(user_id):
        return jsonify({'error': 'Unauthorized: Only the creator can delete this job.'}), 403
        
    db.session.delete(job)
    db.session.commit()
    return '', 204
