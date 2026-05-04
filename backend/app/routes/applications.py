"""Application/candidate management API endpoints."""
import os
import re
import uuid
import shutil
from flask import Blueprint, request, jsonify, current_app, send_file

from app import db
from app.models import JobPosting, Application
from app.nlp.resume_parser import ResumeParser
from app.nlp.ner_extractor import NERExtractor
from app.nlp.matching_engine import MatchingEngine
from app.nlp.preprocessing import TextPreprocessor
from app.nlp.section_classifier import SectionClassifier

applications_bp = Blueprint('applications', __name__)
resume_parser = ResumeParser()
ner_extractor = NERExtractor()
matching_engine = MatchingEngine()
preprocessor = TextPreprocessor(lowercase=True, remove_stop_words=True)
section_classifier = SectionClassifier()


def _find_term_positions(text: str, term: str):
    """Find case-insensitive term occurrences with start/end offsets."""
    if not text or not term:
        return []
    escaped = re.escape(term.strip())
    if not escaped:
        return []

    # Use word boundaries for single token terms; phrase terms can match naturally.
    pattern = rf"\b{escaped}\b" if " " not in term.strip() else escaped
    matches = re.finditer(pattern, text, flags=re.IGNORECASE)
    positions = []
    for m in matches:
        positions.append([m.start(), m.end()])
    return positions


def _extract_keyword_overlap(job_text: str, resume_text: str, max_terms: int = 20):
    """Find lexical overlaps between job and resume after preprocessing."""
    job_tokens = {
        t for t in preprocessor.tokenize(job_text)
        if len(t) >= 3 and not t.isdigit()
    }
    resume_tokens = {
        t for t in preprocessor.tokenize(resume_text)
        if len(t) >= 3 and not t.isdigit()
    }
    overlap = sorted(job_tokens.intersection(resume_tokens))
    return overlap[:max_terms]


def _extract_negated_keywords_positions(text: str, keywords):
    """Return positions for explicitly negated keyword mentions."""
    out = {}
    if not text:
        return out
    text_lower = text.lower()
    for kw in keywords:
        k = str(kw).strip().lower()
        if not k:
            continue
        escaped = re.escape(k)
        pattern = rf"\b{escaped}\b" if " " not in k else escaped
        for m in re.finditer(pattern, text_lower, flags=re.IGNORECASE):
            left_ctx = text_lower[max(0, m.start() - 48):m.start()]
            both_ctx = text_lower[max(0, m.start() - 48):min(len(text_lower), m.end() + 16)]
            if ner_extractor._has_negation_cue(left_ctx) or ner_extractor._has_negation_cue(both_ctx):
                out.setdefault(k, []).append([m.start(), m.end()])
    return out


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
        job_text = f"{job.title} {job.description} {' '.join(job.requirements or [])}"
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
    """Get resume text with explainable score report and keyword highlights."""
    application = Application.query.get_or_404(app_id)
    job = JobPosting.query.get_or_404(application.job_posting_id)

    job_text = f"{job.title} {job.description} {' '.join(job.requirements or [])}"
    resume_text = application.resume_text or ""
    score_report = matching_engine.explain_score(job_text, resume_text)

    matched_skills = score_report.get("skills", {}).get("matched_skills", [])
    negated_required_skills = score_report.get("skills", {}).get("negated_required_skills", [])
    lexical_overlap = _extract_keyword_overlap(job_text, resume_text, max_terms=25)

    matching_skill_positions = {}
    for skill in matched_skills:
        positions = _find_term_positions(resume_text, skill)
        if positions:
            matching_skill_positions[skill] = positions

    matching_keyword_positions = dict(matching_skill_positions)
    for keyword in lexical_overlap:
        if keyword in negated_required_skills:
            continue
        if keyword in matching_keyword_positions:
            continue
        positions = _find_term_positions(resume_text, keyword)
        if positions:
            matching_keyword_positions[keyword] = positions

    negated_keyword_positions = _extract_negated_keywords_positions(
        resume_text,
        negated_required_skills,
    )

    sections = section_classifier.extract_sections(resume_text)
    scoring_breakdown = {
        "final_score_percent": round(float(score_report.get("final_score", 0.0)) * 100, 2),
        "base_score_percent": round(float(score_report.get("base_score_before_skill_adjustment", 0.0)) * 100, 2),
        "weights": score_report.get("weights", {}),
        "tfidf_raw": round(float(score_report.get("tfidf", {}).get("raw_similarity", 0.0)), 4),
        "tfidf_percent": round(float(score_report.get("tfidf", {}).get("calibrated_similarity", 0.0)) * 100, 2),
        "skill_overlap_ratio": round(float(score_report.get("skills", {}).get("skill_overlap_ratio", 0.0)), 4),
        "skill_multiplier": round(float(score_report.get("skills", {}).get("skill_multiplier", 1.0)), 4),
    }

    return jsonify({
        'resume_text': resume_text,
        'matching_skills': matching_skill_positions,
        'matching_keywords': matching_keyword_positions,
        'matched_count': len(matched_skills),
        'job_skill_count': int(score_report.get("skills", {}).get("job_skill_count", 0)),
        'matched_skills': matched_skills,
        'negated_required_skills': negated_required_skills,
        'negated_keyword_positions': negated_keyword_positions,
        'lexical_overlap_keywords': lexical_overlap,
        'sections': sections,
        'scoring_report': scoring_breakdown,
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
        f"{job.title} {job.description} {' '.join(job.requirements or [])}",
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
