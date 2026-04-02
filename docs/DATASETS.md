# Resume Datasets

## Recommended Sources

### Kaggle
1. **Resume Dataset** (Gauravdutt)
   - https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset
   - Various formats

2. **Resume Data PDF** (Hadik)
   - https://www.kaggle.com/datasets/hadikp/resume-data-pdf
   - PDF format

3. **Resume Dataset** (Snehaanbhawal)
   - Used for PDF extraction tasks

### GitHub
- **Resume-extraction-and-candidate-job-matching**
  - https://github.com/swathi-karanth/resume-extraction-and-candidate-job-matching
  - Uses Kaggle dataset with PDF extraction

## Download Instructions

1. Create a Kaggle account at kaggle.com
2. Install Kaggle CLI: `pip install kaggle`
3. Add API credentials to `~/.kaggle/kaggle.json`
4. Download: `kaggle datasets download -d gauravduttakiit/resume-dataset`
5. Extract to `data/resumes/` for testing

### Optional: scripted Kaggle download

If you already have Kaggle CLI configured, you can run:
- `./scripts/download_kaggle_resumes.ps1`

Example (PDF-focused dataset):
- `./scripts/download_kaggle_resumes.ps1 -Dataset "hadikp/resume-data-pdf" -OutDir "data/resumes"`

## Sample Data

For quick testing without downloading, create sample files in:
- `data/sample_resumes/`

Formats: PDF, DOCX, TXT

This repository also includes a couple of small sample `.txt` resumes under `data/sample_resumes/` for local TF-IDF matching and parser smoke tests.
