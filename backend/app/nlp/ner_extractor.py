"""NER-based extraction of skills and experience from resumes using spaCy."""
from typing import Dict, List, Set
import re


class NERExtractor:
    """Extract skills and experience using spaCy NER."""

    # Skill-related entity labels and patterns
    ORG_LABEL = 'ORG'
    PERSON_LABEL = 'PERSON'
    DATE_LABEL = 'DATE'
    GPE_LABEL = 'GPE'
    WORK_OF_ART = 'WORK_OF_ART'

    # Common skill section headers
    SKILL_HEADERS = [
        'skills', 'technical skills', 'core competencies', 'expertise',
        'technologies', 'tools', 'programming languages', 'key skills',
        'professional skills', 'summary of skills', 'competencies'
    ]

    # Common experience section headers
    EXPERIENCE_HEADERS = [
        'experience', 'work experience', 'employment', 'professional experience',
        'career', 'work history', 'employment history'
    ]

    def __init__(self):
        self._nlp = None

    @property
    def nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load('en_core_web_sm')
            except OSError:
                # Download model if not present
                import spacy
                from spacy.cli import download
                download('en_core_web_sm')
                self._nlp = spacy.load('en_core_web_sm')
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
                other_headers = [h for h in self.SKILL_HEADERS + self.EXPERIENCE_HEADERS + ['education', 'summary', 'objective', 'references'] if h != header]
                for oh in other_headers:
                    pos = rest.lower().find('\n' + oh)
                    if pos >= 0:
                        rest = rest[:pos]
                return rest.strip()
        return ''

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume using NER and pattern matching.

        Combines:
        - Entities from skill section
        - Common tech terms (programming languages, tools)
        - Noun chunks in skill section
        """
        skills = set()

        # Extract skill section
        skill_section = self._extract_section_content(text, self.SKILL_HEADERS)
        if skill_section:
            doc = self.nlp(skill_section[:5000])
            # Add noun chunks and significant terms
            for chunk in doc.noun_chunks:
                if len(chunk.text) > 2 and len(chunk.text) < 50:
                    skills.add(chunk.text.strip().lower())
            for token in doc:
                if token.pos_ in ('NOUN', 'PROPN') and len(token.text) > 2:
                    skills.add(token.text.strip().lower())

        # Common tech skills pattern
        tech_patterns = [
            r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|go|rust|php|swift|kotlin)\b',
            r'\b(react|angular|vue|node\.?js|django|flask|spring|express)\b',
            r'\b(sql|mysql|postgresql|mongodb|redis|aws|docker|kubernetes|git)\b',
            r'\b(machine learning|nlp|data science|tensorflow|pytorch|pandas|numpy)\b',
            r'\b(html|css|rest api|graphql|agile|scrum|jira)\b',
        ]
        full_text = text.lower()
        for pattern in tech_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            skills.update(matches)

        # Add ORG entities (companies often indicate domain skills)
        entities = self.extract_entities(text)
        # Company names can help domain-match, but normalize to lowercase for intersections.
        skills.update(s.strip().lower() for s in entities['organizations'][:5])  # Limit

        # Normalize whitespace and casing (keeps matching consistent across job/resume).
        normalized = set()
        for s in skills:
            s2 = re.sub(r"\s+", " ", str(s)).strip().lower()
            if s2:
                normalized.add(s2)

        return sorted(list(normalized))[:50]  # Limit to 50 skills

    def extract_experience(self, text: str) -> List[Dict]:
        """
        Extract work experience entries.

        Returns list of dicts with: company, role, duration (if detectable)
        """
        experience = []
        entities = self.extract_entities(text)

        exp_section = self._extract_section_content(text, self.EXPERIENCE_HEADERS)
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
