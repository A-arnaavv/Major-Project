# AI/ML Part 2 – Interview Intelligence

## 1. Module Overview

This module handles the **Interview Intelligence** part of InterviewGPT.

The main responsibility of this module is to conduct an AI-powered technical interview, evaluate candidate answers, dynamically adjust interview difficulty, track performance, and generate a final performance report.

Current implementation uses the **Gemini API** for LLM-based question generation, answer evaluation, and performance summarization.

---

# 2. Current Project Structure

The main code is located inside:

```text
ai_ml/interview_intelligence/
```

Important files:

```text
interview_intelligence/
│
├── adaptive_engine.py
├── evaluator.py
├── performance_summary.py
├── prompts.py
├── question_generator.py
├── report_generator.py
├── schemas.py
├── session.py
│
└── tests/
    ├── test_adaptive_engine.py
    ├── test_evaluator.py
    ├── test_interview_flow.py
    ├── test_question_generator.py
    └── test_session.py
```

The API layer is currently located at:

```text
backend/
├── __init__.py
└── main.py
```

---

# 3. Features Completed

## AI Interviewer

The system can generate technical interview questions dynamically using Gemini.

Questions are generated based on:

* Interview topic
* Current difficulty
* Previously asked questions

Previously asked questions are supplied to the question generator to reduce repetition.

---

## LLM-Based Answer Evaluation

Candidate answers are evaluated using Gemini.

Each answer receives structured scores for:

* Technical Accuracy
* Relevance
* Clarity
* Completeness
* Overall Score

All scores are normalized to a 0–10 scale.

---

## Strengths and Weaknesses

For every candidate answer, the evaluator generates:

* Strengths
* Weaknesses
* Constructive feedback
* Improved answer

This information is stored as part of the interview history.

---

## Adaptive Difficulty

Three difficulty levels are currently supported:

```text
easy
medium
hard
```

Difficulty changes according to candidate performance.

Current rules:

```text
Overall score < 5
→ decrease difficulty

Overall score between 5 and 7
→ keep same difficulty

Overall score > 7
→ increase difficulty
```

Boundary protection is implemented.

Examples:

```text
easy + low score
→ remains easy

hard + high score
→ remains hard
```

The deterministic adaptive engine is the final authority for difficulty transitions.

---

## Interview Session Management

`InterviewSession` manages the interview lifecycle.

It currently tracks:

* Topic
* Current difficulty
* Current question
* Question number
* Total questions
* Candidate answers
* Evaluation results
* Difficulty transitions
* Interview history

The evaluation rubric/expected concepts are stored internally.

They are **not exposed to the candidate through the API**.

---

## Interview Completion

An interview can be configured with a fixed number of questions.

Example:

```text
total_questions = 5
```

After the final answer, the system stops generating new questions and produces the final report.

---

## Numerical Performance Report

At the end of an interview, the system calculates:

* Total questions
* Average overall score
* Average technical accuracy
* Average relevance
* Average clarity
* Average completeness
* Strengths
* Weaknesses

Topic-level performance tracking is currently being improved.

---

## AI Performance Summary

Gemini is also used to generate a higher-level interview summary.

The summary can contain:

* Overall performance level
* Strong areas
* Weak areas
* Recommended study topics
* Final feedback

This complements the deterministic numerical report.

---

# 4. Current Interview Flow

The current high-level flow is:

```text
Start Interview
      ↓
Generate Question
      ↓
Candidate Answers
      ↓
Gemini Answer Evaluation
      ↓
Structured Scores
      ↓
Strengths / Weaknesses
      ↓
Feedback + Improved Answer
      ↓
Adaptive Difficulty Engine
      ↓
Generate Next Question
      ↓
Repeat Until Interview Complete
      ↓
Numerical Report
      ↓
AI Performance Summary
```

---

# 5. Backend API

A FastAPI backend has been added so that the Interview Intelligence module can be used by the frontend and other project modules.

Main file:

```text
backend/main.py
```

Current endpoints include:

```text
GET /
```

Used to check whether the API is running.

```text
POST /interview/start
```

Starts a new interview and returns the first question.

```text
POST /interview/answer
```

Submits the candidate answer.

The backend evaluates the answer, adjusts the difficulty and, while the interview is still active, returns the next question.

When the interview finishes, it returns the final report instead.

```text
GET /interview/{session_id}/next
```

Can generate the next question for an existing session.

This may eventually become unnecessary because `/interview/answer` can automatically return the next question.

```text
GET /interview/{session_id}/report
```

Returns the numerical report and AI-generated performance summary for an interview session.

---

# 6. Environment Setup

Clone/pull the repository and move to the project root.

Create a Python virtual environment if one does not already exist:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 7. Gemini Configuration

Create a `.env` file in the project root.

Example:

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_available_gemini_model
```

Do NOT commit `.env`.

`.gitignore` should contain:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
.DS_Store
```

The Gemini model is configurable because model availability and free-tier quotas may differ between accounts/projects.

---

# 8. Running the CLI Interview Test

From the project root with the virtual environment activated:

```bash
python3 -m ai_ml.interview_intelligence.tests.test_interview_flow
```

This runs the interview directly in the terminal.

---

# 9. Running the Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

The development server should start on:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to test all API endpoints without a frontend.

---

# 10. Example API Flow

Start an interview using:

```text
POST /interview/start
```

Example request:

```json
{
  "session_id": "candidate001",
  "topic": "Machine Learning",
  "difficulty": "medium",
  "total_questions": 3
}
```

The API returns the first question.

The candidate-facing response intentionally does not expose the expected concepts used for evaluation.

Submit an answer using:

```text
POST /interview/answer
```

Example:

```json
{
  "session_id": "candidate001",
  "candidate_answer": "Candidate answer here"
}
```

For an active interview, the response contains:

* Evaluation
* Next difficulty
* Next question

After the final question, the response contains:

* Final answer evaluation
* Numerical report
* AI performance summary

---

# 11. Important Gemini API Note

Gemini API requests are subject to rate limits and quotas.

During development, we encountered a `429 Rate Limit / Quota Exceeded` response on one Gemini model.

Changing to another available model allowed development to continue.

Because each interview can make multiple LLM calls, avoid unnecessarily long interviews while testing.

For example, a question can require:

```text
Question generation → 1 Gemini request
Answer evaluation   → 1 Gemini request
```

The final AI performance summary can require another request.

For development, 1–3 question interviews are recommended.

---

# 12. Work Currently Pending

The main remaining AI/ML Part 2 work includes:

## Subtopic / Skill Tracking

Instead of storing only a broad topic such as:

```text
Machine Learning
```

questions should also identify specific skills/subtopics such as:

```text
Regularization
Classification Metrics
Bias-Variance Tradeoff
Decision Trees
Model Evaluation
```

This will allow much better skill-level analytics.

---

## Personalized Learning Recommendations

The existing AI summary can recommend study topics, but this needs to be strengthened using:

* Subtopic performance
* Repeated weaknesses
* Technical accuracy
* Difficulty level
* Interview history

The goal is to recommend exactly what the candidate should study next.

---

## Multi-Agent Architecture

The Interview Intelligence system still needs to be organized into the project's multi-agent workflow.

Potential responsibilities include:

```text
Interviewer Agent
        ↓
Evaluation Agent
        ↓
Adaptive Difficulty Logic
        ↓
Recommendation / Feedback Agent
```

The exact architecture should be finalized while integrating with the rest of the team's AI/ML modules.

---

## Reliability

Additional robustness is required for:

* Gemini 429 errors
* API failures
* Retry/backoff
* Invalid LLM responses
* Invalid interview states
* Duplicate answer submissions
* Missing sessions

---

## Automated Testing

Additional automated tests are needed.

A mock LLM/dev mode would be useful so that the interview pipeline can be tested without consuming Gemini API quota.

---

## AI/ML Part 1 Integration

This module must eventually consume context produced by the other AI/ML module, including where appropriate:

* Resume information
* RAG/retrieved context
* Company context
* Role/job information
* Company-specific interview questions/context

Interview Intelligence should consume these outputs rather than duplicate the AI/ML Part 1 implementation.

---

# 13. Data Useful for Analytics Team

Interview history currently provides useful fields such as:

```text
question_number
question
candidate_answer
difficulty
expected_concepts
technical_accuracy
relevance
clarity
completeness
overall_score
strengths
weaknesses
feedback
improved_answer
next_difficulty
```

These can later be stored in the project's database and consumed by the analytics/dashboard modules.

Possible visualizations include:

* Average interview score
* Technical accuracy over time
* Performance by skill/subtopic
* Difficulty progression
* Strongest skills
* Weakest skills
* Candidate improvement over multiple interviews

---

# 14. Current Limitations

Current session storage in the FastAPI backend is in memory.

This means:

```text
Server restart
→ active sessions are lost
```

Persistent database/session storage has not yet been implemented.

The current backend is primarily an integration/demo API for the Interview Intelligence module.

---

# 15. Current Status

The core Interview Intelligence pipeline is functional.

Completed major functionality includes:

```text
Question Generation                 ✓
LLM Answer Evaluation               ✓
Structured Scoring                  ✓
Adaptive Difficulty                 ✓
Strength / Weakness Detection       ✓
Constructive Feedback               ✓
Improved Answer Generation          ✓
Session Tracking                    ✓
Interview Completion                ✓
Numerical Final Report              ✓
AI Performance Summary              ✓
FastAPI Integration                 ✓
Hidden Evaluation Rubric            ✓
```

Major remaining areas:

```text
Subtopic / Skill Tracking           In Progress
Advanced Learning Recommendations   In Progress
Multi-Agent Workflow                Pending
Reliability / Error Handling        Partial
Mock / Automated Testing            Partial
AI/ML Part 1 Integration            Pending
Final Documentation / Cleanup       Pending
```

The current code provides a working foundation for the Interview Intelligence component and is ready for continued development and integration with the other InterviewGPT modules.
