"""Application/candidate management API endpoints."""
import os
import uuid
import shutil
from flask import Blueprint, request, jsonify, current_app, send_file

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
    applications = Application.query.filter_by(job_posting_id=job_id).all()
    applications = sorted(applications, key=lambda a: a.compatibility_score, reverse=True)
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
    ext = os.path.splitext(file.filename)[1].lower()
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_folder, safe_filename)

    try:
        file.save(filepath)
        parsed = resume_parser.parse(filepath)
        resume_text = parsed['text']
        contact = parsed['contact_info']

        # If extraction/OCR still yields no meaningful text, avoid silently
        # creating a "0.00%" application.
        if not resume_text or not resume_text.strip():
            return jsonify({
                'error': (
                    'Could not extract any text from the uploaded PDF. '
                    'If it is image-based, install Poppler + Tesseract (OCR) '
                    'or ensure the PDF contains selectable text.'
                )
            }), 422

        # NER extraction
        extracted = ner_extractor.extract_all(resume_text)

        # Compute compatibility score
        job_text = f"{job.title} {job.description} {job.requirements or ''}"
        score = matching_engine.compute_similarity(job_text, resume_text)

        application = Application(
            job_posting_id=job_id,
            candidate_name=request.form.get('candidate_name') or contact.get('email', 'Unknown'),
            candidate_email=request.form.get('candidate_email') or contact.get('email', ''),
            resume_text=resume_text,
            resume_filename=file.filename,
            compatibility_score=score,
            extracted_skills=extracted['skills'],
            extracted_experience=extracted['experience'],
        )
        db.session.add(application)
        db.session.commit()

        # Keep a permanent copy of the file named with the application ID
        permanent_filepath = os.path.join(upload_folder, f"app_{application.id}{ext}")
        shutil.copy2(filepath, permanent_filepath)

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


@applications_bp.route('/<int:app_id>/resume', methods=['GET'])
def download_resume(app_id):
    """Download or view the uploaded resume file."""
    application = Application.query.get_or_404(app_id)
    upload_folder = get_upload_folder()

    for ext in ResumeParser.SUPPORTED_EXTENSIONS:
        path = os.path.join(upload_folder, f"app_{app_id}{ext}")
        if os.path.exists(path):
            mimetype = 'application/pdf' if ext == '.pdf' else None
            return send_file(
                os.path.abspath(path),
                as_attachment=False,
                download_name=application.resume_filename,
                mimetype=mimetype
            )

    return jsonify({'error': 'Resume file not found on server.'}), 404


@applications_bp.route('/<int:app_id>', methods=['DELETE'])
def delete_application(app_id):
    """Delete an application."""
    app = Application.query.get_or_404(app_id)
    db.session.delete(app)
    db.session.commit()

    # Clean up the saved resume file
    upload_folder = get_upload_folder()
    for ext in ResumeParser.SUPPORTED_EXTENSIONS:
        path = os.path.join(upload_folder, f"app_{app_id}{ext}")
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

    return '', 204


@applications_bp.route('/<int:app_id>/highlights', methods=['GET'])
def get_highlights(app_id):
    """Get resume text with matching skills highlighted."""
    application = Application.query.get_or_404(app_id)
    job = JobPosting.query.get_or_404(application.job_posting_id)

    # Extract skills from job requirements
    job_text = f"{job.title} {job.description} {job.requirements or ''}"
    job_skills = set(ner_extractor.extract_skills(job_text))

    # Get already-extracted resume skills
    resume_skills = set(application.extracted_skills or [])

    # Find matching skills (case-insensitive)
    matching_skills = []
    for skill in resume_skills:
        if any(skill.lower() == js.lower() for js in job_skills):
            matching_skills.append(skill)

    # Find all positions of matching skills in resume text
    resume_text = application.resume_text or ""
    skill_positions = {}

    for skill in matching_skills:
        positions = []
        search_text = resume_text.lower()
        skill_lower = skill.lower()
        start = 0

        while True:
            pos = search_text.find(skill_lower, start)
            if pos == -1:
                break
            positions.append([pos, pos + len(skill)])
            start = pos + 1

        if positions:
            skill_positions[skill] = positions

    return jsonify({
        'resume_text': resume_text,
        'matching_skills': skill_positions,
        'matched_count': len(matching_skills),
        'job_skill_count': len(job_skills),
    })


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
            # API contract: show percent (0..100)
            d['compatibility_score'] = round(float(r['compatibility_score']) * 100, 2)
            result.append(d)

    return jsonify(result)
