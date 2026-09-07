from app.rag.qa import answer_question


question = "What are the candidate's strongest technical skills?"


answer = answer_question(question)


print("\n----- ANSWER -----\n")

print(answer)