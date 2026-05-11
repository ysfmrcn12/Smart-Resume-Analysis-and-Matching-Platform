"""NER-based extraction of skills and experience from resumes using spaCy."""
import os
import re
import json
from pathlib import Path
from typing import Dict, List

from app.nlp.nlp_terms import (
    SKILL_HEADERS,
    EXPERIENCE_HEADERS,
    SKILL_ALIASES,
    TECH_PATTERNS,
    NEGATION_WORDS,
    GENERIC_WORDS,
    NOISE_KEYWORDS
)


class NERExtractor:
    """Extract skills and experience using spaCy NER."""

    # Skill-related entity labels and patterns
    ORG_LABEL = 'ORG'
    PERSON_LABEL = 'PERSON'
    DATE_LABEL = 'DATE'
    GPE_LABEL = 'GPE'
    SKILL_LABEL = 'SKILL'
    WORK_OF_ART = 'WORK_OF_ART'

    def __init__(self, model_name: str = None):
        self._nlp = None
        self._matcher = None
        # Allows loading a fine-tuned spaCy model from disk or package name.
        self.model_name = model_name or os.getenv('NER_MODEL_PATH', 'en_core_web_sm')

    @property
    def nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None:
            local_path = Path(__file__).resolve().parent.parent.parent / "models" / self.model_name
            try:
                import spacy
                if local_path.exists():
                    self._nlp = spacy.load(local_path)
                else:
                    self._nlp = spacy.load(self.model_name)
            except OSError:
                if self.model_name != 'en_core_web_sm':
                    raise
                # Download default model if not present
                import spacy
                from spacy.cli import download
                download('en_core_web_sm')
                self._nlp = spacy.load('en_core_web_sm')
                
            from spacy.matcher import PhraseMatcher
            self._matcher = PhraseMatcher(self._nlp.vocab, attr="LOWER")
            db_path = Path(__file__).resolve().parent.parent.parent / "data" / "skills_db.json"
            if db_path.exists():
                with open(db_path, "r", encoding="utf-8") as f:
                    skill_list = json.load(f)
                # Efficiently load thousands of exact-match terms into the matcher
                patterns = list(self._nlp.tokenizer.pipe(skill_list))
                self._matcher.add("DATABASE_SKILLS", patterns)
        return self._nlp

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        doc = self.nlp(text[:100000])  # Limit length for performance
        entities = {
            'organizations': [],
            'persons': [],
            'dates': [],
            'locations': [],
            'skills': []
        }

        for ent in doc.ents:
            if ent.label_ == self.ORG_LABEL:
                entities['organizations'].append(ent.text.strip())
            elif ent.label_ == self.PERSON_LABEL:
                entities['persons'].append(ent.text.strip())
            elif ent.label_ == self.DATE_LABEL:
                entities['dates'].append(ent.text.strip())
            elif ent.label_ == self.GPE_LABEL:
                entities['locations'].append(ent.text.strip())
            elif ent.label_ == self.SKILL_LABEL:
                entities['skills'].append(ent.text.strip().lower())

        # Deduplicate
        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))

        return entities

    def _extract_section_content(self, text: str, headers: List[str]) -> str:
        """Extract content after a section header."""
        text_lower = text.lower()
        for header in headers:
            idx = text_lower.find(header)
            if idx >= 0:
                start = idx + len(header)
                rest = text[start:start + 5000]
                # Stop at next common section (exclude current header)
                other_headers = [h for h in SKILL_HEADERS + EXPERIENCE_HEADERS + ['education', 'summary', 'objective', 'references'] if h != header]
                for oh in other_headers:
                    pos = rest.lower().find('\n' + oh)
                    if pos >= 0:
                        rest = rest[:pos]
                return rest.strip()
        return ''
        
    def _is_negated(self, text: str, start_pos: int, window: int = 40) -> bool:
        """Check if the text immediately preceding the term contains negation keywords."""
        # Look at the characters just before the skill
        preceding_text = text[max(0, start_pos - window):start_pos].lower()
        # Pad with a space so we can match whole words easily
        preceding_text = re.sub(r'\s+', ' ', preceding_text)
        preceding_text = " " + preceding_text

        return any(neg in preceding_text for neg in NEGATION_WORDS)

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume using NER and pattern matching.

        Combines:
        - Common tech terms (programming languages, tools)
        - Custom NER Model
        - Knowledge Base Matching
        """
        skills = set()

        full_text = text.lower()
        for pattern in TECH_PATTERNS:
            # Use finditer instead of findall so we know EXACTLY where the word is
            for match in re.finditer(pattern, full_text, re.IGNORECASE):
                if not self._is_negated(full_text, match.start()):
                    skills.add(match.group(0))

        # Add ORG entities (companies often indicate domain skills)
        entities = self.extract_entities(text)
        # Company names can help domain-match, but normalize to lowercase for intersections.
        skills.update(s.strip().lower() for s in entities['organizations'][:5])  # Limit
        
        # CRITICAL: Use the Custom NER model we trained to find skills in the whole text!
        doc_full = self.nlp(text[:100000])
        
        # Check against the massive Knowledge Base
        if self._matcher:
            matches = self._matcher(doc_full)
            for match_id, start, end in matches:
                span = doc_full[start:end]
                if not self._is_negated(text, span.start_char):
                    skills.add(span.text.strip().lower())

        for ent in doc_full.ents:
            if ent.label_ == self.SKILL_LABEL:
                if not self._is_negated(text, ent.start_char):
                    skills.add(ent.text.strip().lower())

        # Normalize whitespace and casing (keeps matching consistent across job/resume).
        normalized = set()
        
        for s in skills:
            # Clean whitespace and strip trailing/leading punctuation
            s2 = re.sub(r"\s+", " ", str(s)).strip().lower()
            s2 = re.sub(r'^[^a-z0-9]+|[^a-z0-9]+$', '', s2)
            
            if not s2 or len(s2.split()) > 3:
                continue
                
            if s2 in GENERIC_WORDS:
                continue
                
            # Filter out phrases containing noise words (e.g. "professional experience"), except valid terms
            if any(noise in s2.split() for noise in NOISE_KEYWORDS) and s2 not in ['user experience', 'customer experience']:
                continue

            # Apply alias mapping to standardize skill names (e.g., html5 -> html)
            s2 = SKILL_ALIASES.get(s2, s2)

            normalized.add(s2)

        return sorted(list(normalized))[:50]  # Limit to 50 skills

    def extract_total_years_experience(self, text: str) -> float:
        """Estimate total years of experience from text (job or resume)."""
        text_lower = text.lower()
        max_years = 0.0

        # 1. Look for explicit mentions (e.g., "5 years of experience", "10+ years")
        patterns = [
            r'(\d+(?:\.\d+)?)\+?\s*years?(?:\s*of)?(?:[a-zA-Z\s]{0,20})?experience',
            r'experience.*?(?:of\s*)?(\d+(?:\.\d+)?)\+?\s*years?'
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text_lower):
                try:
                    years = float(match.group(1))
                    if years < 40:  # Sanity check to ignore ridiculous numbers
                        max_years = max(max_years, years)
                except ValueError:
                    pass

        # 2. Look for year ranges in the experience section
        exp_section = self._extract_section_content(text, EXPERIENCE_HEADERS)
        if exp_section:
            years = [int(y) for y in re.findall(r'\b(19[8-9]\d|20[0-2]\d)\b', exp_section)]
            if years:
                import datetime
                min_year = min(years)
                max_year = datetime.datetime.now().year if re.search(r'\b(present|current|now|till date|to date)\b', exp_section.lower()) else max(years)
                span = float(max_year - min_year)
                if 0 < span < 40:
                    max_years = max(max_years, span)

        return max_years

    def extract_experience(self, text: str) -> List[Dict]:
        """
        Extract work experience entries.

        Returns list of dicts with: company, role, duration (if detectable)
        """
        experience = []
        entities = self.extract_entities(text)

        exp_section = self._extract_section_content(text, EXPERIENCE_HEADERS)
        if not exp_section:
            exp_section = text  # Fallback to full text

        doc = self.nlp(exp_section[:8000])
        orgs = entities['organizations']
        dates = entities['dates']

        # Simple extraction: pair organizations with nearby dates
        for i, org in enumerate(orgs[:10]):
            entry = {
                'company': org,
                'role': '',
                'duration': dates[i] if i < len(dates) else ''
            }
            experience.append(entry)

        # If no orgs from NER, try to find role patterns
        if not experience:
            lines = exp_section.split('\n')
            for line in lines[:20]:
                line = line.strip()
                if len(line) > 10 and any(c.isupper() for c in line):
                    experience.append({
                        'company': line[:80],
                        'role': '',
                        'duration': ''
                    })

        return experience[:10]

    def extract_all(self, text: str) -> Dict:
        """Extract all resume information using NER."""
        return {
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'entities': self.extract_entities(text),
        }
