import csv
import json
import re
import ast
from pathlib import Path
import spacy

def main():
    csv_path = "resume_dataset.csv" 

    # Use a blank spaCy model just for its tokenization logic
    nlp = spacy.blank("en")
    
    # This is the output file that train_ner.py will use
    jsonl_path = "skills_ner.jsonl"
    
    valid_records = 0
    
    print(f"Reading dataset from {csv_path}...")
    try:
        with open(csv_path, 'r', encoding='utf-8') as f_in, \
             open(jsonl_path, 'w', encoding='utf-8') as f_out:
            
            reader = csv.DictReader(f_in)
            for row in reader:
                # 1. Prepare the "Question" (The natural text)
                text_parts = []
                if row.get('career_objective') and row['career_objective'].strip() != 'N/A':
                    text_parts.append(row['career_objective'].strip())
                if row.get('responsibilities') and row['responsibilities'].strip() != 'N/A':
                    text_parts.append(row['responsibilities'].strip())
                
                text = "\n\n".join(text_parts)
                if not text:
                    continue
                
                # 2. Prepare the "Answers" (The exact skills)
                skills_str = row.get('skills', '[]')
                try:
                    # Convert "['Skill 1', 'Skill 2']" string into a real Python list
                    skills_list = ast.literal_eval(skills_str)
                except (ValueError, SyntaxError):
                    continue
                
                doc = nlp.make_doc(text)
                # 3. Find the exact start and end positions of the skills in the text
                entities = []
                for skill in skills_list:
                    if not isinstance(skill, str) or len(skill) < 2:
                        continue
                    
                    # Find all matches in the text (ignoring case)
                    for match in re.finditer(re.escape(skill), text, re.IGNORECASE):
                        # Use doc.char_span to create a valid spaCy span.
                        # This ensures the match aligns with token boundaries.
                        # If it doesn't align, char_span returns None.
                        span = doc.char_span(match.start(), match.end(), label="SKILL")
                        if span is not None:
                            entities.append([span.start_char, span.end_char, span.label_])
                
                # 3.5 FILTER OVERLAPPING SPANS
                # spaCy will crash if entities overlap. We sort by start index, then longest span.
                entities.sort(key=lambda x: (x[0], -(x[1] - x[0])))
                filtered_entities = []
                last_end = -1
                for start, end, label in entities:
                    if start >= last_end:
                        filtered_entities.append([start, end, label])
                        last_end = end

                # 4. Save the "flashcard" if we found at least one skill in the text
                if filtered_entities:
                    record = {"text": text, "entities": filtered_entities}
                    f_out.write(json.dumps(record) + '\n')
                    valid_records += 1
                    
        print(f"Success! Created {valid_records} high-quality training examples in '{jsonl_path}'")
    except FileNotFoundError:
        print(f"Error: Could not find the file '{csv_path}'. Please check the path and try again.")

if __name__ == "__main__":
    main()
