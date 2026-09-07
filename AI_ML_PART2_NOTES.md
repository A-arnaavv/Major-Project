# AI/ML Part 2 – Interview Intelligence

## 1. Module Overview

This module handles the **Interview Intelligence** part of InterviewGPT.

Its main responsibility is to conduct an AI-powered technical interview, evaluate candidate answers, dynamically adjust interview difficulty, track performance, generate final reports, and produce personalized learning recommendations.

The current implementation uses the **Gemini API** for real LLM-based:

* Question generation
* Answer evaluation
* Performance summarization

A deterministic **mock mode** is also available for local development and automated testing without consuming Gemini API quota.

---

# 2. Current Project Structure

The main implementation is located inside:

```text
ai_ml/interview_intelligence/
```

Current structure:

```text
interview_intelligence/
│
├── __init__.py
├── adaptive_engine.py
├── config.py
├── evaluator.py
├── gemini_utils.py
├── learning_recommender.py
├── performance_summary.py
├── prompts.py
├── question_generator.py
├── report_generator.py
├── schemas.py
├── session.py
├── orchestrator.py
│
├── agents/
│   ├── __init__.py
│   ├── interviewer_agent.py
│   ├── evaluator_agent.py
│   └── recommendation_agent.py
│
└── tests/
    ├── test_gemini_utils.py
    ├── test_mock_pipeline.py
    └── test_session.py
```

The manual CLI interview script is stored separately so that pytest does not collect it as an automated test:

```text
ai_ml/interview_intelligence/tests/manual_interview_flow.py
```

The API layer is located at:

```text
backend/
├── __init__.py
└── main.py
```

---

# 3. Features Completed

## AI Interviewer

The system generates technical interview questions dynamically.

Question generation takes into account:

* Interview topic
* Current difficulty
* Previously asked questions
* Resume context
* Target job role
* Company context
* Retrieved/RAG context

Previously asked questions are passed to the generator to reduce repetition.

In real mode, Gemini can use the supplied Part 1 context to personalize questions.

In mock mode, deterministic questions are selected from a local question bank.

---

## LLM-Based Answer Evaluation

Candidate answers are evaluated using Gemini in real mode.

Each answer receives structured scores for:

* Technical Accuracy
* Relevance
* Clarity
* Completeness
* Overall Score

All scores use a **0–10 scale**.

The evaluator also generates:

* Strengths
* Weaknesses
* Constructive feedback
* Improved answer
* Difficulty recommendation

The Gemini difficulty recommendation is advisory.

The deterministic adaptive difficulty engine remains the final authority for difficulty transitions.

---

## Mock Evaluation Mode

The project supports:

```text
LLM_MODE=mock
```

Mock mode allows the entire interview pipeline to run without Gemini API calls.

This is useful for:

* Local development
* Automated testing
* Debugging
* Avoiding rate limits
* Avoiding unnecessary API quota usage

Mock evaluation is intentionally deterministic.

For example:

```text
No meaningful answer
→ overall score = 0
→ next recommendation = easier
```

A meaningful mock answer currently receives a deterministic score so that the full pipeline can be tested consistently.

---

## Strengths and Weaknesses

For each candidate answer, the evaluator produces:

* Strengths
* Weaknesses
* Constructive feedback
* Improved answer

This information is stored in the interview history and later contributes to final performance reporting.

---

## Adaptive Difficulty

Three difficulty levels are supported:

```text
easy
medium
hard
```

Difficulty changes according to the candidate's overall evaluation score.

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

The deterministic adaptive engine is the final authority.

---

## Interview Session Management

`InterviewSession` manages the complete interview lifecycle.

It tracks:

* Topic
* Current difficulty
* Current question
* Question number
* Total questions
* Candidate answers
* Expected concepts
* Evaluation results
* Difficulty transitions
* Interview history
* Resume context
* Job role
* Company context
* Retrieved context

The current question and its expected concepts are maintained server-side.

The candidate only submits:

```text
candidate_answer
```

This prevents the frontend from modifying the question or expected evaluation rubric before submission.

---

## Interview Completion

An interview can be configured with a fixed number of questions.

Example:

```text
total_questions = 5
```

After the final answer:

* No additional interview question is required
* Numerical performance statistics are generated
* AI performance summary is generated
* Personalized learning recommendations are generated

---

## Numerical Performance Report

At the end of the interview, the deterministic report generator calculates:

* Total questions
* Average overall score
* Average technical accuracy
* Average relevance
* Average clarity
* Average completeness
* Strengths
* Weaknesses
* Subtopic performance

The numerical report does not depend on Gemini.

---

## Subtopic / Skill Tracking

Question generation now identifies a specific subtopic for each question.

Examples include:

```text
Bias-Variance Tradeoff
Supervised Learning
Overfitting
Model Evaluation
Classification Metrics
Regularization
Model Generalization
Data Leakage
Advanced Model Evaluation
```

Each interview record stores both:

```text
topic
subtopic
```

The report generator calculates average performance for each subtopic.

This enables skill-level analytics instead of relying only on broad topics such as:

```text
Machine Learning
```

---

## AI Performance Summary

Gemini can generate a higher-level final performance summary.

The summary contains:

* Overall performance
* Strong areas
* Weak areas
* Recommended topics
* Final feedback

Example output structure:

```python
{
    "overall_performance": "...",
    "strong_areas": [...],
    "weak_areas": [...],
    "recommended_topics": [...],
    "final_feedback": "..."
}
```

A deterministic mock version is also available during development and automated testing.

---

## Personalized Learning Recommendations

A deterministic learning recommendation engine is implemented.

It takes:

```text
subtopic_performance
```

and produces a prioritized study plan.

Example structure:

```python
{
    "priority": 1,
    "subtopic": "Bias-Variance Tradeoff",
    "current_score": 2.0,
    "performance_level": "Critical",
    "recommended_action": "Study the fundamentals before attempting advanced questions."
}
```

Current performance levels include:

```text
Strong
Moderate
Weak
Critical
```

Topics with lower scores receive higher learning priority.

---

# 4. Multi-Agent Architecture

Interview Intelligence now uses a basic multi-agent architecture.

Current structure:

```text
InterviewSession
        │
        ▼
InterviewOrchestrator
        │
        ├───────────────┐
        │               │
        ▼               ▼
InterviewerAgent   EvaluatorAgent
        │
        │
        └───────────────┐
                        ▼
              RecommendationAgent
```

The orchestrator coordinates specialist agents while keeping the session responsible for overall interview state.

---

## InterviewerAgent

Responsible for:

* Generating interview questions
* Receiving topic and difficulty
* Receiving previous questions
* Receiving optional Part 1 context
* Returning structured generated questions

---

## EvaluatorAgent

Responsible for:

* Evaluating candidate answers
* Returning structured numerical scores
* Identifying strengths and weaknesses
* Generating feedback
* Producing an improved answer

---

## RecommendationAgent

Responsible for:

* Receiving subtopic performance
* Generating prioritized learning recommendations
* Highlighting the weakest skills first

---

## Adaptive Difficulty Logic

Adaptive difficulty remains deterministic and separate from the LLM agents.

This avoids allowing the LLM alone to control interview progression.

---

# 5. Part 1 Integration Contract

AI/ML Part 2 can now consume optional context produced by AI/ML Part 1.

Supported fields:

```python
resume_context: str | None
job_role: str | None
company_context: str | None
retrieved_context: str | None
```

Example:

```python
session = InterviewSession(
    topic="Machine Learning",
    difficulty="medium",
    total_questions=5,
    resume_context="Python and NLP experience",
    job_role="ML Engineer",
    company_context="Recommendation systems",
    retrieved_context="Embeddings and ranking models",
)
```

Responsibilities remain separated between both AI/ML modules.

### AI/ML Part 1 Responsibility

Part 1 may handle:

* Resume parsing
* Resume analysis
* Embeddings
* Vector database
* RAG
* Company research/context
* Role/job context
* Company-specific retrieval

### AI/ML Part 2 Responsibility

Part 2 consumes that context and uses it for:

* Question generation
* Interview personalization
* Adaptive interviewing
* Candidate evaluation
* Performance reporting
* Learning recommendations

Part 2 does **not** duplicate resume parsing, RAG, embeddings, or company research.

---

# 6. Current Interview Flow

The complete interview flow is:

```text
Part 1 Context
      │
      ▼
Start Interview
      │
      ▼
InterviewSession
      │
      ▼
InterviewOrchestrator
      │
      ▼
InterviewerAgent
      │
      ▼
Generate Question
      │
      ▼
Candidate Answer
      │
      ▼
EvaluatorAgent
      │
      ▼
Gemini / Mock Evaluation
      │
      ▼
Structured Scores
      │
      ├── Technical Accuracy
      ├── Relevance
      ├── Clarity
      ├── Completeness
      └── Overall Score
      │
      ▼
Strengths / Weaknesses
      │
      ▼
Feedback + Improved Answer
      │
      ▼
Adaptive Difficulty Engine
      │
      ▼
Generate Next Question
      │
      ▼
Repeat Until Complete
      │
      ▼
Numerical Report
      │
      ▼
Subtopic Performance
      │
      ▼
AI Performance Summary
      │
      ▼
RecommendationAgent
      │
      ▼
Personalized Learning Plan
```

---

# 7. Backend API

A FastAPI backend exposes the Interview Intelligence module to the frontend and other project modules.

Main file:

```text
backend/main.py
```

Current endpoints:

```text
GET /
POST /interview/start
POST /interview/answer
GET /interview/{session_id}/next
GET /interview/{session_id}/report
```

---

## GET /

Used to verify that the service is running.

Example:

```text
GET /
```

---

## POST /interview/start

Starts a new interview and generates the first question.

The endpoint accepts both normal interview configuration and optional Part 1 context.

Example request:

```json
{
  "session_id": "candidate_001",
  "topic": "Machine Learning",
  "difficulty": "medium",
  "total_questions": 5,
  "resume_context": "Candidate has experience with Python and NLP.",
  "job_role": "Machine Learning Engineer",
  "company_context": "Company works on recommendation systems.",
  "retrieved_context": "Relevant retrieved topics include embeddings and ranking models."
}
```

Example response structure:

```json
{
  "session_id": "candidate_001",
  "status": "started",
  "question": "Generated interview question",
  "difficulty": "medium",
  "topic": "Machine Learning",
  "subtopic": "Recommendation Systems"
}
```

Expected concepts are intentionally not returned to the candidate.

---

## POST /interview/answer

Submits the candidate's answer.

Example:

```json
{
  "session_id": "candidate_001",
  "candidate_answer": "Candidate answer here"
}
```

For an active interview, the API returns:

* Evaluation
* Next difficulty
* Next question

For a completed interview, the API returns:

* Final answer evaluation
* Numerical report
* AI performance summary
* Personalized learning plan

---

## GET /interview/{session_id}/next

Generates the next question for an existing interview session.

This endpoint may eventually become optional because:

```text
POST /interview/answer
```

already returns the next question during the normal interview flow.

---

## GET /interview/{session_id}/report

Returns:

* Numerical report
* AI performance summary
* Learning plan

for the specified interview session.

---

# 8. Environment Setup

Clone or pull the repository and move to the project root.

Create a virtual environment if required:

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

# 9. Environment Configuration

Create a `.env` file in the project root.

Example:

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_available_gemini_model
LLM_MODE=mock
```

Do not commit `.env`.

`.gitignore` should contain:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
.DS_Store
```

---

# 10. Mock Mode

For normal development and automated testing, use:

```text
LLM_MODE=mock
```

Advantages:

* No Gemini requests
* No Gemini quota usage
* Fast tests
* Deterministic behavior
* Easier debugging
* Reliable regression testing

Mock mode should normally remain enabled while developing locally.

---

# 11. Real Gemini Mode

For real LLM testing:

```text
LLM_MODE=real
```

Real mode uses Gemini for:

```text
Question Generation
Answer Evaluation
Performance Summary
```

The configured Gemini model is loaded from:

```text
GEMINI_MODEL
```

The API key is loaded from:

```text
GEMINI_API_KEY
```

After real-mode smoke testing, it is recommended to switch back to:

```text
LLM_MODE=mock
```

for normal development.

---

# 12. Gemini Reliability Layer

A centralized Gemini reliability helper is implemented in:

```text
gemini_utils.py
```

Gemini calls from:

```text
question_generator.py
evaluator.py
performance_summary.py
```

use the shared helper.

The reliability layer handles transient failures such as:

```text
408
429
500
502
503
504
```

and connection failures.

Retry behavior uses:

* Limited retry attempts
* Exponential backoff
* Small randomized delay/jitter

The retry count is intentionally small so that failures do not create excessive API usage.

---

## Invalid LLM Responses

Structured Gemini responses are validated using Pydantic.

If Gemini returns invalid structured output, the system converts it into a controlled:

```text
RuntimeError
```

instead of silently accepting malformed data.

---

## API Error Handling

The FastAPI layer handles:

* Missing sessions
* Invalid session states
* Completed interviews
* Gemini/runtime failures

Appropriate HTTP errors are returned instead of allowing uncontrolled application crashes.

---

# 13. Running Automated Tests

From the project root:

```bash
python3 -m pytest ai_ml/interview_intelligence/tests -v
```

Current validated result:

```text
16 passed
```

Automated coverage currently includes:

* Gemini reliability helper
* Retry behavior
* Connection failure handling
* Mock question generation
* Question non-repetition
* Mock empty-answer evaluation
* Mock meaningful-answer evaluation
* Adaptive difficulty
* Learning-plan prioritization
* Session question generation
* Answer submission
* Session history
* Interview completion
* Final report generation
* Learning plan generation
* Part 1 context integration

---

# 14. Real Gemini Smoke Test

A complete real-mode smoke test has been successfully performed.

The test used Part 1-style context including:

```text
Resume Context:
Python and NLP experience

Job Role:
ML Engineer

Company Context:
Recommendation systems

Retrieved Context:
Embeddings and ranking models
```

Gemini generated a context-aware question about recommendation-system cold-start problems and embeddings.

The candidate answer intentionally discussed the unrelated bias-variance tradeoff.

Gemini correctly identified the answer as irrelevant.

Observed behavior included:

```text
Question:
Context-aware recommendation-system question

Difficulty:
medium

Evaluation:
Very low score due to irrelevance

Adaptive Transition:
medium → easy

Final Summary:
Needs Significant Improvement
```

This validated the real end-to-end flow:

```text
Part 1 Context
→ InterviewerAgent
→ Gemini Question Generation
→ Candidate Answer
→ EvaluatorAgent
→ Gemini Structured Evaluation
→ Adaptive Difficulty
→ Gemini Performance Summary
```

---

# 15. Running the Manual CLI Interview

The manual CLI interview is intentionally not named with the pytest `test_` prefix.

Run:

```bash
python3 -m ai_ml.interview_intelligence.tests.manual_interview_flow
```

This allows an interactive terminal interview without pytest attempting to capture `input()`.

---

# 16. Running the Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

Development server:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to test the entire API without a frontend.

---

# 17. Data Available for Analytics Team

Interview history provides fields that can later be stored in the project database.

Important fields include:

```text
question_number
question
candidate_answer
topic
subtopic
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

These support analytics such as:

* Average interview score
* Technical accuracy over time
* Relevance over time
* Clarity over time
* Completeness over time
* Performance by subtopic
* Difficulty progression
* Strongest skills
* Weakest skills
* Candidate improvement across interviews
* Learning recommendation trends

The analytics team can consume stored interview-history records without changing the Interview Intelligence evaluation logic.

---

# 18. Important Architecture Rule

Production code must never import anything from:

```text
tests/
```

Correct dependency direction:

```text
tests/
   │
   ▼
production code
```

Incorrect:

```text
production code
   │
   ▼
tests/
```

This rule prevents circular imports and keeps test-only code isolated from the application.

---

# 19. Current Limitations

## In-Memory Session Storage

FastAPI currently stores sessions in:

```python
sessions: Dict[str, InterviewSession]
```

This means:

```text
Server Restart
→ Active sessions are lost
```

Persistent database/session storage has not yet been implemented.

The current backend should therefore be treated as the Interview Intelligence integration/demo API until database integration is completed.

---

## Part 1 Context Format

Part 1 integration currently accepts context as optional strings:

```text
resume_context
job_role
company_context
retrieved_context
```

This interface is intentionally simple for initial integration.

The team can later replace or extend these fields with structured schemas once the final Part 1 implementation is merged.

---

## Mock Evaluator

Mock evaluation is deterministic and intentionally simple.

It is designed for:

```text
testing
development
regression validation
```

It is not intended to reproduce the full semantic reasoning quality of Gemini.

---

# 20. Current Status

The core Interview Intelligence component is now functionally complete for the assigned AI/ML Part 2 scope.

Current status:

```text
Question Generation                    ✓ Complete
LLM Answer Evaluation                  ✓ Complete
Structured Scoring                     ✓ Complete
Adaptive Difficulty                    ✓ Complete
Strength / Weakness Detection          ✓ Complete
Constructive Feedback                  ✓ Complete
Improved Answer Generation             ✓ Complete
Session Tracking                       ✓ Complete
Interview Completion                   ✓ Complete
Numerical Final Report                 ✓ Complete
AI Performance Summary                 ✓ Complete
Subtopic / Skill Tracking              ✓ Complete
Personalized Learning Recommendations  ✓ Complete
Multi-Agent Workflow                   ✓ Complete
Gemini Reliability / Retry Layer       ✓ Complete
Mock LLM Mode                          ✓ Complete
Automated Testing                      ✓ 16 Passing
FastAPI Integration                    ✓ Complete
Hidden Evaluation Rubric               ✓ Complete
AI/ML Part 1 Integration Contract      ✓ Complete
Real Gemini Smoke Test                 ✓ Passed
```

---

# 21. Remaining Work

The remaining work is primarily full-project integration and final polish rather than core AI/ML Part 2 development.

Remaining areas include:

```text
Persistent Database Integration        Pending Team Integration
Frontend Integration                   Pending Team Integration
Final Part 1 Data Contract Refinement  Pending Team Merge
Analytics Data Persistence             Pending Team Integration
Full-System End-to-End Testing         Pending Team Integration
Final Documentation / Demo Cleanup     Minor
```

These areas depend partly on other project modules and are not missing core Interview Intelligence functionality.

---

# 22. Handoff Summary

AI/ML Part 2 now provides a working Interview Intelligence system that can:

```text
Accept Part 1 Candidate Context
        ↓
Generate Personalized Questions
        ↓
Evaluate Candidate Answers
        ↓
Produce Structured Scores
        ↓
Adjust Difficulty Dynamically
        ↓
Track Subtopic Performance
        ↓
Generate Final Reports
        ↓
Produce AI Performance Summary
        ↓
Generate Personalized Learning Recommendations
```

The component has been validated in both:

```text
Mock Mode
Real Gemini Mode
```

and currently has:

```text
16 passing automated tests
```

The module is ready for integration with the remaining InterviewGPT components.
