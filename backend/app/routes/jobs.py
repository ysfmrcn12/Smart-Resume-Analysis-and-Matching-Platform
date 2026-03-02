"""Job posting CRUD API endpoints."""
from flask import Blueprint, request, jsonify

from app import db
from app.models import JobPosting

jobs_bp = Blueprint('jobs', __name__)


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
        title=data['title'],
        description=data['description'],
        requirements=data.get('requirements', ''),
        company=data.get('company', ''),
        location=data.get('location', ''),
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
        job.title = data['title']
    if 'description' in data:
        job.description = data['description']
    if 'requirements' in data:
        job.requirements = data['requirements']
    if 'company' in data:
        job.company = data['company']
    if 'location' in data:
        job.location = data['location']

    db.session.commit()
    return jsonify(job.to_dict())


@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job posting."""
    job = JobPosting.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return '', 204
