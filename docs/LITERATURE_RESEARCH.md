# Literature Research: Resume Parsing and NLP Techniques

## 1. Overview

Resume parsing and candidate-job matching leverage Natural Language Processing (NLP) to automate HR screening. This document summarizes key techniques and approaches used in the field.

## 2. Core NLP Techniques

### 2.1 Named Entity Recognition (NER)

- **Purpose**: Identifies and classifies key information: names, organizations, locations, dates, skills, qualifications
- **Implementation**: spaCy provides pre-trained NER models (en_core_web_sm, en_core_web_lg)
- **Resume-specific entities**: PERSON, ORG, GPE, DATE, SKILL (custom trained)
- **Reference**: Hybrid approaches combine rule-based, ML, and transformer-based NER

### 2.2 TF-IDF (Term Frequency-Inverse Document Frequency)

- **Purpose**: Feature extraction, text representation for similarity computation
- **Formula**: TF-IDF(t,d) = TF(t,d) × IDF(t) where IDF = log(N/df_t)
- **Use case**: Convert resume text and job descriptions to vectors for cosine similarity
- **Implementation**: scikit-learn TfidfVectorizer

### 2.3 Cosine Similarity

- **Purpose**: Measure semantic/textual similarity between resume and job description
- **Formula**: cos(θ) = (A·B) / (||A|| × ||B||)
- **Range**: 0 (no similarity) to 1 (identical)
- **Application**: Core metric for candidate-job matching score

### 2.4 spaCy NER Models

- **en_core_web_sm**: Lightweight, fast, suitable for production
- **en_core_web_lg**: Higher accuracy, larger model
- **Custom training**: Possible to train on resume-specific entities (skills, experience)

## 3. Advanced Approaches (2024)

### 3.1 BERT-Based NLP

- Tokenizers generate feature vectors for job descriptions and resume keywords
- Achieves screening speeds ~1 resume/second
- Preprocessing: keyword extraction, stop word removal, stemming, lemmatization

### 3.2 Hybrid Models

- **Rule-based**: Patterns for phone numbers, emails, skills
- **Machine Learning**: CRF-based NER
- **Transformers**: BERT/spaCy for contextual understanding

## 4. Data Preprocessing Pipeline

1. **Text Normalization**: Lowercase, Unicode handling
2. **Tokenization**: Split text into tokens
3. **Stop Word Removal**: Remove common words (the, is, at)
4. **Lemmatization/Stemming**: Reduce words to root form
5. **Special Character Handling**: Clean punctuation and symbols

## 5. Resume Datasets

| Source | Format | Description |
|--------|--------|-------------|
| Kaggle - Gauravdutt | Various | Resume Dataset |
| Kaggle - Hadik | PDF | Resume Data PDF |
| Kaggle - Snehaanbhawal | PDF | For extraction tasks |
| GitHub - ResumeRevealer | PDF, DOC, JPG, HTML | 200 pre-annotated resumes |

## 6. File Format Support

- **PDF**: PyPDF2, pdfplumber, PDFMiner
- **DOCX**: python-docx
- **TXT**: Native Python file reading

## 7. References

- Building a Resumé Analyzer with NER (Medium)
- Applying BERT-Based NLP for Automated Resume Screening (Springer, 2024)
- NLP-Based AI-Driven Resume Screening Solution (Springer, 2024)
- JennyTan5522/NLP-Resume-Parsing (GitHub)
- Swathi-Karanth/Resume-extraction-and-candidate-job-matching (GitHub)
