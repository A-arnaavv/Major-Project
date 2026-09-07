from app.interview.question_generator import (
    generate_interview_questions
)


questions = generate_interview_questions(
    interview_type="technical",
    num_questions=5
)


print("\n----- INTERVIEW QUESTIONS -----\n")

print(questions)