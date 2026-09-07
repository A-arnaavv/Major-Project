from ai_ml.part1.paths import DEFAULT_RESUME_PATH
from ai_ml.part1.resume.parser import extract_text_from_pdf


def test_extract_text_from_resume_pdf():
    assert DEFAULT_RESUME_PATH.exists()

    text = extract_text_from_pdf(
        str(DEFAULT_RESUME_PATH)
    )

    assert isinstance(text, str)
    assert text.strip()
    assert len(text) > 100
