import csv
import json
import ast
from pathlib import Path

def main():
    csv_path = "resume_dataset.csv"
    
    # Save the database in a new 'data' folder inside the backend
    out_path = Path(__file__).resolve().parent.parent / "data" / "skills_db.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    unique_skills = set()

    print(f"Reading {csv_path} to build massive Knowledge Base...")
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                skills_str = row.get('skills', '[]')
                try:
                    skills_list = ast.literal_eval(skills_str)
                    for skill in skills_list:
                        # Keep valid strings that aren't entire sentences
                        if isinstance(skill, str) and 2 <= len(skill.strip()) <= 40:
                            unique_skills.add(skill.strip().lower())
                except (ValueError, SyntaxError):
                    continue
    except FileNotFoundError:
        print(f"Error: Could not find '{csv_path}'. Run this script where your CSV is located.")
        return

    # Filter out pure noise words
    noise = {'experience', 'skill', 'skills', 'knowledge', 'ability', 'years'}
    cleaned_skills = [s for s in unique_skills if s not in noise]

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(sorted(cleaned_skills), f, indent=2)

if __name__ == "__main__":
    main()