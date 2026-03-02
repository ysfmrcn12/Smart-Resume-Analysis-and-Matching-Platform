"""API routes."""
from app.routes.jobs import jobs_bp
from app.routes.applications import applications_bp
from app.routes.nlp import nlp_bp

from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Register sub-blueprints
api_bp.register_blueprint(jobs_bp, url_prefix='/jobs')
api_bp.register_blueprint(applications_bp, url_prefix='/applications')
api_bp.register_blueprint(nlp_bp, url_prefix='/nlp')
