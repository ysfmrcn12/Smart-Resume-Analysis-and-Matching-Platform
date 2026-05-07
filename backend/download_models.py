"""Script to pre-download all AI models for offline use."""
import os
from pathlib import Path

def main():
    models_dir = Path(__file__).resolve().parent / 'models'
    models_dir.mkdir(exist_ok=True)

    print("1. Downloading Sentence Transformer model (Semantic Search)...")
    from sentence_transformers import SentenceTransformer
    st_model_name = 'all-MiniLM-L6-v2'
    st_path = models_dir / st_model_name
    model = SentenceTransformer(st_model_name)
    model.save(str(st_path))
    print(f"✅ Saved Sentence Transformer to {st_path}\n")

    print("2. Downloading spaCy NER model...")
    import spacy
    from spacy.cli import download
    spacy_model_name = 'en_core_web_sm'
    spacy_path = models_dir / spacy_model_name
    download(spacy_model_name)
    nlp = spacy.load(spacy_model_name)
    nlp.to_disk(spacy_path)
    print(f"✅ Saved spaCy NER model to {spacy_path}\n")

    print("🎉 All models downloaded successfully! The application will now use these local folders and will not require an internet connection on startup.")

if __name__ == '__main__':
    main()