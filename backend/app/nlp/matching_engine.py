"""Matching engine for explainable job-resume relevance scoring."""
import math
from typing import Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.nlp.preprocessing import TextPreprocessor
from app.nlp.ner_extractor import NERExtractor


class MatchingEngine:
    """Score and rank candidates with explainable hybrid scoring."""

    def __init__(self, max_features: int = 5000, ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize matching engine.

        Args:
            max_features: Max features for TF-IDF
            ngram_range: N-gram range (1,2) = unigrams and bigrams
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words='english',
            min_df=1,
            max_df=1.0,
            sublinear_tf=True,
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
    def _calibrate_similarity(raw_similarity: float, k: float = 10.0) -> float:
        """
        Calibrate cosine similarity into a human-friendlier range.

        TF-IDF cosine values are often small for relevant pairs, so we use a
        saturating transform to improve score spread in the mid range.
        """
        raw_similarity = max(0.0, min(1.0, raw_similarity))
        return 1.0 - math.exp(-k * raw_similarity)

    def _compute_tfidf_similarity(self, job_processed: str, resume_processed: str) -> float:
        """Compute raw TF-IDF cosine similarity for one pair."""
        self.vectorizer.fit([job_processed, resume_processed])
        job_vec = self.vectorizer.transform([job_processed])
        resume_vec = self.vectorizer.transform([resume_processed])
        return float(cosine_similarity(job_vec, resume_vec)[0][0])

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
            skill_multiplier = 0.5
        else:
            # Base multiplier from 0.5 to 1.0 based on overlap
            skill_multiplier = 0.5 + 0.5 * skill_overlap_ratio
            # Add a slight bonus for matching multiple skills
            skill_multiplier += min(0.2, overlap * 0.05)

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
                # Penalty if they have no detectable experience but the job requires it
                exp_multiplier = 0.7
            else:
                # Proportional penalty
                ratio = cand_exp / req_exp
                exp_multiplier = 0.7 + (0.3 * ratio)
                
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
            "weights": {"tfidf": 1.0},
            "tfidf": {"raw_similarity": 0.0, "calibrated_similarity": 0.0},
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
            raw_tfidf = self._compute_tfidf_similarity(job_processed, resume_processed)
            tfidf_calibrated = self._calibrate_similarity(raw_tfidf)
        except Exception:
            raw_tfidf = 0.0
            tfidf_calibrated = 0.0

        tfidf_weight = 1.0
        base_score = tfidf_calibrated

        skill_metrics = self._compute_skill_metrics(job_text, resume_text)
        exp_metrics = self._compute_experience_metrics(job_text, resume_text)
        final = self._clamp_float(base_score * skill_metrics["skill_multiplier"] * exp_metrics["experience_multiplier"])

        return {
            "final_score": final,
            "base_score_before_skill_adjustment": self._clamp_float(base_score),
            "weights": {
                "tfidf": tfidf_weight,
            },
            "tfidf": {
                "raw_similarity": self._clamp_float(raw_tfidf),
                "calibrated_similarity": self._clamp_float(tfidf_calibrated),
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

        # Create a corpus for TF-IDF: [job, resume1, resume2, ...]
        corpus = [job_processed] + [r[2] for r in resume_data]

        try:
            # Fit the vectorizer once on all documents
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            job_vec = tfidf_matrix[0]
            resume_vecs = tfidf_matrix[1:]

            # Compute all similarities at once
            raw_similarities = cosine_similarity(job_vec, resume_vecs)[0]
        except Exception:
            # Fallback if vectorization fails (e.g., all texts are empty)
            raw_similarities = [0.0] * len(resumes)

        scores = []
        for i, (rid, resume_text, resume_processed) in enumerate(resume_data):
            if not resume_text or not resume_processed:
                scores.append((rid, 0.0))
                continue

            raw_tfidf = raw_similarities[i]
            tfidf_calibrated = self._calibrate_similarity(raw_tfidf)
            base_score = tfidf_calibrated
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
