"""Matching engine using TF-IDF and cosine similarity for job-resume matching."""
from typing import Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.nlp.preprocessing import TextPreprocessor
from app.nlp.ner_extractor import NERExtractor


class MatchingEngine:
    """Score and rank candidates based on job-resume compatibility."""

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

    def _preprocess(self, text: str) -> str:
        """Preprocess text for vectorization."""
        return self.preprocessor.preprocess_for_tfidf(text)

    def compute_similarity(self, job_text: str, resume_text: str) -> float:
        """
        Compute cosine similarity between job description and resume.

        Args:
            job_text: Job description/requirements text
            resume_text: Resume text

        Returns:
            Similarity score between 0 and 1
        """
        if not job_text or not resume_text:
            return 0.0

        job_processed = self._preprocess(job_text)
        resume_processed = self._preprocess(resume_text)

        if not job_processed or not resume_processed:
            return 0.0

        try:
            # Fit vectorizer only on the job text to keep IDF stable across resume sets.
            self.vectorizer.fit([job_processed])
            job_vec = self.vectorizer.transform([job_processed])
            resume_vec = self.vectorizer.transform([resume_processed])
            similarity = cosine_similarity(job_vec, resume_vec)[0][0]
            # Compute skill overlap to penalize unrelated resumes
            try:
                job_skills = set(self.extractor.extract_skills(job_text))
                resume_skills = set(self.extractor.extract_skills(resume_text))
            except Exception:
                job_skills = set()
                resume_skills = set()

            overlap = len(job_skills.intersection(resume_skills))
            job_skill_count = max(1, len(job_skills))
            skill_overlap_ratio = overlap / job_skill_count

            # If no skill overlap, apply a penalty; otherwise boost by overlap
            if skill_overlap_ratio == 0:
                final = float(similarity) * 0.25
            else:
                final = float(similarity) * (0.6 + 0.4 * skill_overlap_ratio)

            return max(0.0, min(1.0, final))
        except Exception:
            return 0.0

    def compute_similarity_batch(
        self,
        job_text: str,
        resumes: List[Tuple[str, str]]  # List of (id, text)
    ) -> List[Tuple[str, float]]:
        """
        Compute similarity scores for multiple resumes against one job.

        Args:
            job_text: Job description
            resumes: List of (identifier, resume_text) tuples

        Returns:
            List of (identifier, score) sorted by score descending
        """
        if not resumes:
            return []

        job_processed = self._preprocess(job_text)
        all_texts = [job_processed]
        ids = []

        for rid, rtext in resumes:
            ids.append(rid)
            all_texts.append(self._preprocess(rtext))

        try:
            # Fit vectorizer only on the job text to prevent resume-to-resume IDF shifts.
            self.vectorizer.fit([job_processed])
            job_vec = self.vectorizer.transform([job_processed])
            # Pre-extract job skills once
            try:
                job_skills = set(self.extractor.extract_skills(job_text))
            except Exception:
                job_skills = set()

            scores = []
            for i, rid in enumerate(ids):
                resume_vec = self.vectorizer.transform([all_texts[i + 1]])
                sim = cosine_similarity(job_vec, resume_vec)[0][0]
                try:
                    resume_skills = set(self.extractor.extract_skills(resumes[i][1]))
                except Exception:
                    resume_skills = set()

                overlap = len(job_skills.intersection(resume_skills))
                job_skill_count = max(1, len(job_skills))
                skill_overlap_ratio = overlap / job_skill_count

                if skill_overlap_ratio == 0:
                    final = float(sim) * 0.25
                else:
                    final = float(sim) * (0.6 + 0.4 * skill_overlap_ratio)

                scores.append((rid, max(0.0, min(1.0, final))))
            return sorted(scores, key=lambda x: x[1], reverse=True)
        except Exception:
            return [(rid, 0.0) for rid in ids]

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
