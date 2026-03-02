"""Application/candidate management API endpoints."""
import os
import uuid
from flask import Blueprint, request, jsonify, current_app

from app import db
from app.models import JobPosting, Application
from app.nlp.resume_parser import ResumeParser
from app.nlp.ner_extractor import NERExtractor
from app.nlp.matching_engine import MatchingEngine

applications_bp = Blueprint('applications', __name__)
resume_parser = ResumeParser()
ner_extractor = NERExtractor()
matching_engine = MatchingEngine()


def get_upload_folder():
    """Get or create upload folder."""
    folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(folder, exist_ok=True)
    return folder


@applications_bp.route('/job/<int:job_id>', methods=['GET'])
def list_applications(job_id):
    """List all applications for a job, sorted by compatibility score."""
    job = JobPosting.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_posting_id=job_id)\
        .order_by(Application.compatibility_score.desc()).all()
    return jsonify([a.to_dict() for a in applications])


@applications_bp.route('/job/<int:job_id>/upload', methods=['POST'])
def upload_resume(job_id):
    """
    Upload a resume for a job posting.

    Accepts: PDF, DOCX, TXT
    Parses resume, extracts skills/experience via NER, computes compatibility score.
    """
    job = JobPosting.query.get_or_404(job_id)

    if 'resume' not in request.files and 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files.get('resume') or request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not ResumeParser.is_supported(file.filename):
        return jsonify({
            'error': 'Unsupported format. Use PDF, DOCX, or TXT.'
        }), 400

    upload_folder = get_upload_folder()
    ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_folder, safe_filename)

    try:
        file.save(filepath)
        parsed = resume_parser.parse(filepath)
        resume_text = parsed['text']
        contact = parsed['contact_info']

        # NER extraction
        extracted = ner_extractor.extract_all(resume_text)

        # Compute compatibility score
        job_text = f"{job.title} {job.description} {job.requirements or ''}"
        score = matching_engine.compute_similarity(job_text, resume_text)

        application = Application(
            job_posting_id=job_id,
            candidate_name=request.form.get('candidate_name') or contact.get('email', 'Unknown'),
            candidate_email=contact.get('email') or request.form.get('candidate_email', ''),
            resume_text=resume_text,
            resume_filename=file.filename,
            compatibility_score=score,
            extracted_skills=extracted['skills'],
            extracted_experience=extracted['experience'],
        )
        db.session.add(application)
        db.session.commit()

        return jsonify(application.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    finally:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass


@applications_bp.route('/<int:app_id>', methods=['GET'])
def get_application(app_id):
    """Get a single application by ID."""
    app = Application.query.get_or_404(app_id)
    return jsonify(app.to_dict())


@applications_bp.route('/<int:app_id>', methods=['DELETE'])
def delete_application(app_id):
    """Delete an application."""
    app = Application.query.get_or_404(app_id)
    db.session.delete(app)
    db.session.commit()
    return '', 204


@applications_bp.route('/job/<int:job_id>/rank', methods=['GET'])
def rank_applicants(job_id):
    """Get ranked list of applicants for a job."""
    job = JobPosting.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_posting_id=job_id).all()

    candidates = [
        {'id': a.id, 'resume_text': a.resume_text}
        for a in applications
    ]
    ranked = matching_engine.rank_candidates(
        f"{job.title} {job.description} {job.requirements or ''}",
        candidates
    )

    # Map back to full application data
    app_map = {a.id: a for a in applications}
    result = []
    for r in ranked:
        app = app_map.get(r['id'])
        if app:
            d = app.to_dict()
            d['compatibility_score'] = r['compatibility_score']
            result.append(d)

    return jsonify(result)
