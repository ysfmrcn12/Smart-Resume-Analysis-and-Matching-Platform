"""Matching engine for explainable job-resume relevance scoring."""
import math
from typing import Dict, List, Tuple
import os
from pathlib import Path
import warnings

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ModuleNotFoundError:
    SentenceTransformer = None
    util = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from app.nlp.preprocessing import TextPreprocessor
from app.nlp.ner_extractor import NERExtractor


class MatchingEngine:
    """Score and rank candidates with explainable hybrid scoring."""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize matching engine.
        """
        self.model = None
        self.uses_semantic_model = False

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            # Determine which model to load with a clear priority
            model_path_to_load = None

            # 1. Prioritize a fine-tuned model from .env
            tuned_model_path_str = os.getenv('SEMANTIC_MODEL_PATH')
            if tuned_model_path_str:
                potential_path = Path(__file__).resolve().parent.parent.parent / tuned_model_path_str
                if potential_path.exists():
                    model_path_to_load = str(potential_path)
                    print(f"INFO: Loading fine-tuned semantic model from: {model_path_to_load}")
                else:
                    print(f"WARNING: SEMANTIC_MODEL_PATH is set but path not found: {potential_path}. Falling back.")

            # 2. Fallback to a pre-downloaded base model
            if not model_path_to_load:
                local_path = Path(__file__).resolve().parent.parent.parent / "models" / model_name
                if local_path.exists():
                    model_path_to_load = str(local_path)
                    print(f"INFO: Loading pre-downloaded base model: {model_path_to_load}")

            # 3. If nothing is found locally, download from Hugging Face Hub
            try:
                self.model = SentenceTransformer(model_path_to_load or model_name)
                self.uses_semantic_model = True
            except Exception as exc:
                warnings.warn(
                    f"Could not initialize sentence-transformers model ({exc}). "
                    "Falling back to TF-IDF similarity.",
                    RuntimeWarning,
                )
        else:
            warnings.warn(
                "sentence-transformers is not installed. Falling back to TF-IDF similarity.",
                RuntimeWarning,
            )

        self.preprocessor = TextPreprocessor(lowercase=True, remove_stop_words=False)
        self.extractor = NERExtractor()
    @staticmethod
    def _clamp_float(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
        """Clamp float value to a range."""
        return max(min_value, min(max_value, value))

    def _preprocess(self, text: str) -> str:
        """Preprocess text for vectorization."""
        return self.preprocessor.preprocess_for_tfidf(text)

    @staticmethod
    def _calibrate_similarity(raw_similarity: float) -> float:
        """
        Calibrate semantic cosine similarity into a human-friendlier range.

        Sentence Transformers typically output scores between 0.15 and 0.85.
        Scores below 0.25 usually indicate no semantic relationship.
        We linearly scale the [0.25, 0.75] range to [0.0, 1.0].
        """
        raw_similarity = max(0.0, min(1.0, raw_similarity))
        
        baseline = 0.25
        if raw_similarity <= baseline:
            return 0.0
            
        calibrated = (raw_similarity - baseline) / 0.5
        return max(0.0, min(1.0, calibrated))

    @staticmethod
    def _compute_tfidf_similarity(job_processed: str, resume_processed: str) -> float:
        """Compute lexical TF-IDF cosine similarity for one pair."""
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        matrix = vectorizer.fit_transform([job_processed, resume_processed])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])

    def _compute_semantic_similarity(self, job_processed: str, resume_processed: str) -> float:
        """Compute sentence-level similarity for one pair."""
        if self.uses_semantic_model and self.model is not None:
            emb1 = self.model.encode(job_processed, convert_to_tensor=True)
            emb2 = self.model.encode(resume_processed, convert_to_tensor=True)
            return float(util.cos_sim(emb1, emb2)[0][0])
        return self._compute_tfidf_similarity(job_processed, resume_processed)

    def _compute_skill_metrics(self, job_text: str, resume_text: str) -> Dict:
        """Extract skill overlap statistics and multiplier."""
        try:
            job_skills = set(self.extractor.extract_skills(job_text))
            resume_skills = set(self.extractor.extract_skills(resume_text))
        except Exception:
            job_skills = set()
            resume_skills = set()

        matched_skills = job_skills.intersection(resume_skills)
        job_skill_count = len(job_skills)
        resume_skill_count = len(resume_skills)
        overlap = len(matched_skills)
        skill_overlap_ratio = overlap / max(1, job_skill_count)

        if job_skill_count == 0:
            # If we could not extract job skills, avoid an arbitrary penalty
            skill_multiplier = 1.0
        elif skill_overlap_ratio == 0:
            skill_multiplier = 0.75  # Softer penalty if 0 skills match exactly
        else:
            # Base multiplier from 0.75 to 1.1 based on overlap
            skill_multiplier = 0.75 + (0.35 * skill_overlap_ratio)
            # Add a slight bonus for exact keyword matches
            skill_multiplier += min(0.15, overlap * 0.03)

        return {
            "job_skills": sorted(job_skills),
            "resume_skills": sorted(resume_skills),
            "matched_skills": sorted(matched_skills),
            "job_skill_count": job_skill_count,
            "resume_skill_count": resume_skill_count,
            "matched_skill_count": overlap,
            "skill_overlap_ratio": skill_overlap_ratio,
            "skill_multiplier": skill_multiplier,
        }

    def _compute_experience_metrics(self, job_text: str, resume_text: str) -> Dict:
        """Compare required years of experience vs candidate's years."""
        req_exp = self.extractor.extract_total_years_experience(job_text)
        cand_exp = self.extractor.extract_total_years_experience(resume_text)
        
        if req_exp == 0:
            # If job doesn't specify experience, multiplier is neutral
            exp_multiplier = 1.0
        else:
            if cand_exp >= req_exp:
                # Bonus for meeting or exceeding experience
                exp_multiplier = 1.1
            elif cand_exp == 0:
                # Softer penalty if NER fails to extract dates
                exp_multiplier = 0.85
            else:
                ratio = cand_exp / req_exp
                exp_multiplier = 0.85 + (0.25 * ratio)
                
        return {
            "required_years": req_exp,
            "candidate_years": cand_exp,
            "experience_multiplier": exp_multiplier,
        }

    def explain_score(self, job_text: str, resume_text: str) -> Dict:
        """
        Return a detailed scoring report for one job/resume pair.

        Uses TF-IDF as the core textual relevance signal and combines it with
        skill overlap logic for the final score.
        """
        empty_report = {
            "final_score": 0.0,
            "base_score_before_skill_adjustment": 0.0,
            "weights": {"semantic": 1.0},
            "semantic": {"raw_similarity": 0.0, "calibrated_similarity": 0.0},
            "skills": {
                "job_skills": [],
                "resume_skills": [],
                "matched_skills": [],
                "job_skill_count": 0,
                "resume_skill_count": 0,
                "matched_skill_count": 0,
                "skill_overlap_ratio": 0.0,
                "skill_multiplier": 1.0,
            },
            "experience": {
                "required_years": 0.0,
                "candidate_years": 0.0,
                "experience_multiplier": 1.0,
            },
        }
        if not job_text or not resume_text:
            return empty_report

        job_processed = self._preprocess(job_text)
        resume_processed = self._preprocess(resume_text)
        if not job_processed or not resume_processed:
            return empty_report

        try:
            raw_semantic = self._compute_semantic_similarity(job_processed, resume_processed)
            semantic_calibrated = (
                self._calibrate_similarity(raw_semantic)
                if self.uses_semantic_model
                else self._clamp_float(raw_semantic)
            )
        except Exception:
            raw_semantic = 0.0
            semantic_calibrated = 0.0

        semantic_weight = 1.0
        base_score = semantic_calibrated

        skill_metrics = self._compute_skill_metrics(job_text, resume_text)
        exp_metrics = self._compute_experience_metrics(job_text, resume_text)
        final = self._clamp_float(base_score * skill_metrics["skill_multiplier"] * exp_metrics["experience_multiplier"])

        return {
            "final_score": final,
            "base_score_before_skill_adjustment": self._clamp_float(base_score),
            "weights": {
                "semantic": semantic_weight,
            },
            "semantic": {
                "raw_similarity": self._clamp_float(raw_semantic),
                "calibrated_similarity": self._clamp_float(semantic_calibrated),
            },
            "skills": skill_metrics,
            "experience": exp_metrics,
        }

    def compute_similarity(self, job_text: str, resume_text: str) -> float:
        """
        Compute cosine similarity between job description and resume.

        Args:
            job_text: Job description/requirements text
            resume_text: Resume text

        Returns:
            Similarity score between 0 and 1
        """
        report = self.explain_score(job_text, resume_text)
        return float(report.get("final_score", 0.0))

    def compute_similarity_batch(
        self,
        job_text: str,
        resumes: List[Tuple[str, str]]  # List of (id, text)
    ) -> List[Tuple[str, float]]:
        """
        Compute similarity scores for multiple resumes against one job efficiently.

        Args:
            job_text: Job description
            resumes: List of (identifier, resume_text) tuples

        Returns:
            List of (identifier, score) sorted by score descending
        """
        if not job_text or not resumes:
            return []

        job_processed = self._preprocess(job_text)
        resume_data = [
            (rid, resume_text, self._preprocess(resume_text))
            for rid, resume_text in resumes
        ]

        try:
            if self.uses_semantic_model and self.model is not None:
                job_emb = self.model.encode(job_processed, convert_to_tensor=True)
                resume_texts = [r[2] for r in resume_data]
                resume_embs = self.model.encode(resume_texts, convert_to_tensor=True)
                raw_similarities = util.cos_sim(job_emb, resume_embs)[0].tolist()
            else:
                raw_similarities = [
                    self._compute_tfidf_similarity(job_processed, resume_processed)
                    for _, _, resume_processed in resume_data
                ]
        except Exception:
            # Fallback if vectorization fails (e.g., all texts are empty)
            raw_similarities = [0.0] * len(resumes)

        scores = []
        for i, (rid, resume_text, resume_processed) in enumerate(resume_data):
            if not resume_text or not resume_processed:
                scores.append((rid, 0.0))
                continue

            raw_semantic = raw_similarities[i]
            semantic_calibrated = (
                self._calibrate_similarity(raw_semantic)
                if self.uses_semantic_model
                else self._clamp_float(raw_semantic)
            )
            base_score = semantic_calibrated
            skill_metrics = self._compute_skill_metrics(job_text, resume_text)
            exp_metrics = self._compute_experience_metrics(job_text, resume_text)
            final_score = self._clamp_float(base_score * skill_metrics["skill_multiplier"] * exp_metrics["experience_multiplier"])
            scores.append((rid, final_score))

        return sorted(scores, key=lambda x: x[1], reverse=True)

    def rank_candidates(
        self,
        job_text: str,
        candidates: List[Dict]
    ) -> List[Dict]:
        """
        Rank candidates by compatibility score.

        Args:
            job_text: Job description (combine title, description, requirements)
            candidates: List of dicts with 'id' and 'resume_text' keys

        Returns:
            Same candidates sorted by score, with 'compatibility_score' added
        """
        if not candidates:
            return []

        resumes = [(c.get('id', i), c.get('resume_text', '')) for i, c in enumerate(candidates)]
        scored = self.compute_similarity_batch(job_text, resumes)

        score_map = {str(rid): score for rid, score in scored}
        for c in candidates:
            cid = str(c.get('id', ''))
            c['compatibility_score'] = round(score_map.get(cid, 0), 2)

        return sorted(candidates, key=lambda x: x['compatibility_score'], reverse=True)
