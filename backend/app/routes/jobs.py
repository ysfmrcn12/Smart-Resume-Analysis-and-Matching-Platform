"""Job posting CRUD API endpoints."""
from flask import Blueprint, request, jsonify

from app import db
from app.models import JobPosting

jobs_bp = Blueprint('jobs', __name__)

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
        return jsonify({'error': 'No data provided'}), 400

    required = ['title', 'description']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    job = JobPosting(
        title=_truncate_str(data['title'], TITLE_MAX_LENGTH),
        description=data['description'],
        requirements=data.get('requirements', '') or '',
        company=_truncate_str(data.get('company', ''), COMPANY_MAX_LENGTH),
        location=_truncate_str(data.get('location', ''), LOCATION_MAX_LENGTH),
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201


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
        job.requirements = data['requirements'] or ''
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
    db.session.delete(job)
    db.session.commit()
    return '', 204
