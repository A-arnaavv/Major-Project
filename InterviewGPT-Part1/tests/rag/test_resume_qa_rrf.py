from app.rag.qa import answer_resume_question


question = "What are the candidate's main Machine Learning skills?"


print("Generating answer...\n")

answer = answer_resume_question(question)


print("\n------ ANSWER ------\n")

print(answer)