"""Fine-tune a Sentence Transformer model on job-resume pairs from the database."""
import os
import sys
from pathlib import Path

# Add the project root to the Python path to allow imports from 'app'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

from app import create_app, db
from app.models import JobPosting, Application


def generate_triplets(min_positive_score=0.6, max_negative_score=0.3, max_triplets_per_job=100):
    """
    Generate (anchor, positive, negative) triplets from the database.
    Anchor: Job Description
    Positive: A good-matching resume
    Negative: A bad-matching resume
    """
    print("INFO: Generating training triplets from database...")
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    with app.app_context():
        jobs = JobPosting.query.all()
        triplets = []

        for job in jobs:
            job_text = f"{job.title} {job.description} {' '.join(job.requirements or [])}"
            applications = Application.query.filter_by(job_posting_id=job.id).all()

            if not applications or len(applications) < 2:
                continue

            positives = [app for app in applications if app.compatibility_score >= min_positive_score]
            negatives = [app for app in applications if app.compatibility_score <= max_negative_score]

            if not positives or not negatives:
                continue

            # Create combinations and limit them
            job_triplets_count = 0
            for pos_app in positives:
                for neg_app in negatives:
                    if job_triplets_count >= max_triplets_per_job:
                        break
                    triplets.append(InputExample(texts=[job_text, pos_app.resume_text, neg_app.resume_text]))
                    job_triplets_count += 1
                if job_triplets_count >= max_triplets_per_job:
                    break

        print(f"INFO: Generated {len(triplets)} triplets for training.")
        return triplets


def main():
    base_model_name = 'all-MiniLM-L6-v2'
    output_path_str = 'models/semantic-search-resume-v1'
    epochs = 2
    batch_size = 16

    output_path = Path(__file__).resolve().parent.parent / output_path_str
    output_path.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(base_model_name)
    train_examples = generate_triplets()

    if not train_examples:
        print("❌ Could not generate training data. Ensure you have jobs with both high-scoring (>60%) and low-scoring (<30%) resumes in your database.")
        return

    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
    train_loss = losses.TripletLoss(model=model)

    print(f"\nStarting fine-tuning for {epochs} epochs...")
    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=epochs, warmup_steps=100, output_path=str(output_path), show_progress_bar=True)

    print(f"\n🎉 Fine-tuning complete! Your new model is saved in: {output_path}")
    print("\nNext steps: Add `SEMANTIC_MODEL_PATH=models/semantic-search-resume-v1` to your .env file and restart the server to use it.")

if __name__ == "__main__":
    main()