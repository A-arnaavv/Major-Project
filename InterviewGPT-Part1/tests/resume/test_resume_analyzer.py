import json

from app.resume.parser import extract_text_from_pdf
from app.resume.analyzer import analyze_resume


pdf_path = "data/raw/Tanishka latest.pdf"

print("Extracting resume text...")

resume_text = extract_text_from_pdf(pdf_path)


print("Analyzing resume with Gemini...")

candidate_profile = analyze_resume(resume_text)


print("\n----- CANDIDATE PROFILE -----\n")

print(json.dumps(candidate_profile, indent=4))


# Save the candidate profile

output_path = "data/processed/candidate_profile.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(candidate_profile, file, indent=4)


print("\nCandidate profile saved successfully!")