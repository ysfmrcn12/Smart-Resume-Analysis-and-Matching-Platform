"""NLP API endpoints for testing and documentation."""
from flask import Blueprint, request, jsonify

from app.nlp.preprocessing import TextPreprocessor
from app.nlp.resume_parser import ResumeParser
from app.nlp.ner_extractor import NERExtractor
from app.nlp.matching_engine import MatchingEngine

nlp_bp = Blueprint('nlp', __name__)
preprocessor = TextPreprocessor()
resume_parser = ResumeParser()
ner_extractor = NERExtractor()
matching_engine = MatchingEngine()


@nlp_bp.route('/preprocess', methods=['POST'])
def preprocess_text():
    """
    Preprocess text for NLP.

    POST body: { "text": "...", "for_ner": false }
    """
    data = request.get_json() or {}
    text = data.get('text', '')
    for_ner = data.get('for_ner', False)
    result = preprocessor.process(text, for_ner=for_ner)
    return jsonify({'preprocessed': result})


@nlp_bp.route('/parse', methods=['POST'])
def parse_resume():
    """
    Parse a resume file (multipart form with 'file' key).

    Supports: PDF, DOCX, TXT
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    if not ResumeParser.is_supported(file.filename):
        return jsonify({'error': 'Unsupported format'}), 400

    import tempfile
    import os
    ext = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        file.save(tmp.name)
        try:
            parsed = resume_parser.parse(tmp.name)
            return jsonify(parsed)
        finally:
            os.unlink(tmp.name)


@nlp_bp.route('/extract', methods=['POST'])
def extract_entities():
    """
    Extract skills and experience from text using NER.

    POST body: { "text": "..." }
    """
    data = request.get_json() or {}
    text = data.get('text', '')
    extracted = ner_extractor.extract_all(text)
    return jsonify(extracted)


@nlp_bp.route('/similarity', methods=['POST'])
def compute_similarity():
    """
    Compute TF-IDF cosine similarity between job and resume.

    POST body: { "job_text": "...", "resume_text": "..." }
    """
    data = request.get_json() or {}
    job_text = data.get('job_text', '')
    resume_text = data.get('resume_text', '')
    score = matching_engine.compute_similarity(job_text, resume_text)
    return jsonify({'similarity_score': round(score, 4)})
