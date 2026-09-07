def create_candidate_document(candidate_profile: dict) -> str:
    """
    Converts the structured candidate profile
    into a text document for the RAG pipeline.
    """

    document = f"""
Candidate Name: {candidate_profile.get("name", "")}

Summary:
{candidate_profile.get("summary", "")}

Technical Skills:
{", ".join(candidate_profile.get("technical_skills", []))}

Programming Languages:
{", ".join(candidate_profile.get("programming_languages", []))}

Libraries and Tools:
{", ".join(candidate_profile.get("libraries_tools", []))}

Databases:
{", ".join(candidate_profile.get("databases", []))}

Projects:
{candidate_profile.get("projects", [])}

Experience:
{candidate_profile.get("experience", [])}

Certifications:
{", ".join(candidate_profile.get("certifications", []))}

Strengths:
{", ".join(candidate_profile.get("strengths", []))}

Improvement Areas:
{", ".join(candidate_profile.get("improvement_areas", []))}
"""

    return document.strip()