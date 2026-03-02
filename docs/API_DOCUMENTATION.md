# API Documentation

Base URL: `http://localhost:5000/api`

## Job Postings

### List Jobs
```
GET /api/jobs
```
Returns all job postings.

### Get Job
```
GET /api/jobs/:id
```

### Create Job
```
POST /api/jobs
Content-Type: application/json

{
  "title": "Software Engineer",
  "description": "We are looking for...",
  "requirements": "Python, React, 3+ years",
  "company": "Acme Inc",
  "location": "Remote"
}
```

### Update Job
```
PUT /api/jobs/:id
Content-Type: application/json
```
Same body as create (partial updates supported).

### Delete Job
```
DELETE /api/jobs/:id
```

## Applications

### List Applications for Job
```
GET /api/applications/job/:job_id
```
Returns applications sorted by compatibility score.

### Upload Resume
```
POST /api/applications/job/:job_id/upload
Content-Type: multipart/form-data

- file or resume: (PDF, DOCX, TXT)
- candidate_name: (optional)
- candidate_email: (optional)
```

### Get Application
```
GET /api/applications/:id
```

### Delete Application
```
DELETE /api/applications/:id
```

### Rank Applicants
```
GET /api/applications/job/:job_id/rank
```
Returns applicants ranked by TF-IDF cosine similarity score.

## NLP Endpoints (Testing)

### Preprocess Text
```
POST /api/nlp/preprocess
Content-Type: application/json

{ "text": "...", "for_ner": false }
```

### Parse Resume
```
POST /api/nlp/parse
Content-Type: multipart/form-data
file: (PDF, DOCX, TXT)
```

### Extract Entities (NER)
```
POST /api/nlp/extract
Content-Type: application/json

{ "text": "..." }
```

### Compute Similarity
```
POST /api/nlp/similarity
Content-Type: application/json

{ "job_text": "...", "resume_text": "..." }
```
