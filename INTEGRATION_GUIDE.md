# InterviewGPT AI – Integration Guide

## Purpose

This document explains how other team members should integrate with the **Interview Intelligence** module implemented under:

```text
ai_ml/interview_intelligence/
```

This module owns:

* AI interviewer flow
* adaptive question difficulty
* LLM-based answer evaluation
* structured scoring
* strengths and weaknesses
* constructive feedback
* improved answer generation
* interview session tracking
* performance summaries
* personalized learning recommendations
* analytics-ready export records
* multi-agent interview orchestration
* Gemini reliability handling
* API input validation
* session-storage abstraction
* safe pending-question retrieval

The module is designed to consume outputs from AI/ML Part 1 and expose structured outputs to backend, analytics, and dashboard components.

---

# 1. System Architecture

The current integration architecture is:

```text
AI/ML Part 1
Resume Analysis + RAG
        ↓
InterviewContext
        ↓
FastAPI Backend
        ↓
SessionStore
        ↓
InterviewSession
        ↓
InterviewOrchestrator
   ├── InterviewerAgent
   ├── EvaluatorAgent
   └── RecommendationAgent
        ↓
Performance + Learning Plan
        ↓
Analytics Exporter
        ↓
Analytics / BI / Database
```

The main principle is separation of responsibilities.

AI/ML Part 1 supplies candidate-, role-, company-, and retrieval-specific context.

AI/ML Part 2 owns the interview intelligence workflow.

The backend exposes Part 2 through HTTP endpoints.

The analytics exporter converts interview results into stable structured records for downstream analytics.

---

# 2. AI/ML Part 1 → Interview Intelligence

The first AI/ML module may provide candidate- and company-specific context.

The expected input contract is represented by:

```text
ai_ml/interview_intelligence/integration_schemas.py
```

Schema:

```python
class InterviewContext(BaseModel):
    topic: str
    difficulty: str = "medium"
    total_questions: int = 5
    resume_context: str | None = None
    job_role: str | None = None
    company_context: str | None = None
    retrieved_context: str | None = None
```

Example:

```json
{
  "topic": "Machine Learning",
  "difficulty": "medium",
  "total_questions": 5,
  "resume_context": "Candidate has experience with Python, NLP and scikit-learn.",
  "job_role": "Machine Learning Engineer",
  "company_context": "The company works on recommendation systems.",
  "retrieved_context": "Relevant retrieved concepts include embeddings, ranking models and cold-start techniques."
}
```

The additional context fields are optional.

If they are not provided, the interview system still works using the topic and difficulty.

The Interview Intelligence module should not perform resume parsing, RAG retrieval, embedding generation, vector search, or company research itself.

Those responsibilities belong to AI/ML Part 1.

---

# 3. Running the API

The FastAPI backend is implemented in:

```text
backend/main.py
```

Run it with:

```bash
uvicorn backend.main:app --reload
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The current API surface is:

```text
GET  /
GET  /health

POST /interview/start
POST /interview/answer

GET  /interview/{session_id}/next
GET  /interview/{session_id}/report
GET  /interview/{session_id}/analytics
```

---

# 4. Service Health

Use:

```text
GET /health
```

The health endpoint provides a lightweight service check without making a Gemini API request.

Example response:

```json
{
  "status": "healthy",
  "service": "Interview Intelligence API",
  "version": "0.1.0",
  "llm_mode": "mock"
}
```

The `llm_mode` field indicates whether the application is currently configured for mock or real Gemini execution.

The endpoint intentionally does not call Gemini, so health monitoring:

* does not consume Gemini quota
* remains fast
* does not depend on temporary external LLM availability

---

# 5. Starting an Interview

Use:

```text
POST /interview/start
```

Example request:

```json
{
  "session_id": "candidate_001",
  "topic": "Machine Learning",
  "difficulty": "medium",
  "total_questions": 5,
  "resume_context": "Python and NLP experience",
  "job_role": "ML Engineer",
  "company_context": "Recommendation systems",
  "retrieved_context": "Embeddings and ranking models"
}
```

Example response:

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

## Request Validation

The API validates interview-start requests before creating a session.

Current rules:

```text
session_id       required non-whitespace text
topic            required non-whitespace text
difficulty       easy | medium | hard
total_questions  minimum 1, maximum 20
```

`session_id` and `topic` are normalized before use.

Leading and trailing whitespace is removed.

Examples:

```text
"  candidate_001  "
→ "candidate_001"

"  Machine Learning  "
→ "Machine Learning"
```

Whitespace-only values such as:

```text
"   "
```

are rejected with HTTP `422`.

Invalid request structures are rejected by FastAPI/Pydantic with HTTP `422`.

Duplicate session IDs are rejected with HTTP `400`.

---

# 6. Submitting Candidate Answers

Use:

```text
POST /interview/answer
```

Example request:

```json
{
  "session_id": "candidate_001",
  "candidate_answer": "The candidate's answer goes here."
}
```

The candidate does not submit the original question or expected concepts.

Those are maintained server-side by the interview session.

This prevents the client from modifying evaluation context.

The evaluation contains:

```json
{
  "technical_accuracy": 7,
  "relevance": 8,
  "clarity": 7,
  "completeness": 6,
  "overall_score": 7.0,
  "strengths": [
    "Relevant explanation"
  ],
  "weaknesses": [
    "Needs more technical depth"
  ],
  "feedback": "Expand the explanation with implementation details.",
  "improved_answer": "A stronger answer would explain...",
  "next_difficulty": "same"
}
```

The Gemini-produced `next_difficulty` field is advisory.

The deterministic adaptive engine is the actual source of truth for the next interview difficulty.

When more questions remain, the API returns the next question automatically.

When the configured question count is reached, it returns the final report.

An empty `candidate_answer` remains valid input.

This is intentional because a no-answer response is a legitimate interview outcome and is handled by the evaluator rather than rejected at the API boundary.

---

# 7. Adaptive Difficulty Logic

Difficulty levels are:

```text
easy
medium
hard
```

Rules:

```text
overall_score > 7  → increase difficulty
overall_score < 5  → decrease difficulty
otherwise          → keep same difficulty
```

Difficulty is bounded between `easy` and `hard`.

Examples:

```text
medium + score 8.0 → hard
medium + score 6.0 → medium
medium + score 3.0 → easy

hard + score 9.0   → hard
easy + score 2.0   → easy
```

This deterministic rule prevents LLM variability from directly controlling interview progression.

---

# 8. Retrieving the Pending Question

Use:

```text
GET /interview/{session_id}/next
```

Example:

```text
GET /interview/candidate_001/next
```

This endpoint returns the currently pending unanswered question for an active interview.

Important behavior:

```text
POST /interview/start
        ↓
Question 1 generated
        ↓
GET /interview/{session_id}/next
        ↓
Question 1 returned again
```

Calling `/next` does **not** generate Question 2 when Question 1 is still pending.

Similarly:

```text
POST /interview/answer
        ↓
Current answer evaluated
        ↓
Question 2 generated
        ↓
GET /interview/{session_id}/next
        ↓
Question 2 returned
```

This prevents the client from accidentally skipping an unanswered question.

If a valid active session has no current question, the endpoint may generate one as a fallback.

Missing sessions return HTTP `404`.

Requests after the interview has completed return HTTP `400`.

---

# 9. Performance Report

Use:

```text
GET /interview/{session_id}/report
```

The report contains:

```text
numerical_report
ai_summary
learning_plan
```

The numerical report contains aggregate metrics such as:

* total questions answered so far
* average score
* average technical accuracy
* average relevance
* average clarity
* average completeness
* subtopic performance

The AI summary contains:

* overall performance
* strong areas
* weak areas
* recommended topics
* final feedback

The learning plan prioritizes weaker subtopics and provides recommended next actions.

The endpoint is intentionally available for both active and completed interviews.

For an active interview:

```text
/report
→ performance so far
```

For a completed interview:

```text
/report
→ final accumulated performance
```

The authoritative final report is also returned automatically when the final interview answer is submitted.

---

# 10. Personalized Learning Recommendations

Learning recommendations are generated from subtopic-level performance.

Lower-performing subtopics receive higher priority.

The current performance categories are:

```text
Score >= 8  → Strong
Score >= 6  → Moderate
Score >= 4  → Weak
Score < 4   → Critical
```

Recommendations become progressively more fundamental as the score decreases.

Examples:

```text
Strong
→ Maintain and practice advanced questions.

Moderate
→ Review key concepts and practice medium-level questions.

Weak
→ Revisit fundamentals and solve guided practice questions.

Critical
→ Study the fundamentals before attempting advanced questions.
```

This output can be consumed directly by frontend learning-plan views or analytics dashboards.

---

# 11. Analytics Integration

Analytics-ready outputs can be obtained through:

```text
GET /interview/{session_id}/analytics
```

Example:

```text
GET /interview/candidate_001/analytics
```

The response contains:

```json
{
  "session_id": "candidate_001",
  "question_records": [],
  "summary": {}
}
```

The exporter implementation is located in:

```text
ai_ml/interview_intelligence/analytics_exporter.py
```

The schemas are defined in:

```text
ai_ml/interview_intelligence/integration_schemas.py
```

The analytics endpoint does not mutate interview state.

It may be used during an active interview to obtain data collected so far, or after completion to obtain the full interview analytics output.

---

# 12. Question-Level Analytics Record

Each interview question is exported using the `QuestionAnalyticsRecord` schema.

Fields include:

```text
session_id
question_number
topic
subtopic
difficulty
question
candidate_answer
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

Example:

```json
{
  "session_id": "candidate_001",
  "question_number": 1,
  "topic": "Machine Learning",
  "subtopic": "Regularization",
  "difficulty": "medium",
  "question": "What is regularization?",
  "candidate_answer": "It helps reduce overfitting.",
  "technical_accuracy": 7,
  "relevance": 8,
  "clarity": 7,
  "completeness": 6,
  "overall_score": 7.0,
  "strengths": [
    "Relevant answer"
  ],
  "weaknesses": [
    "Needs more detail"
  ],
  "feedback": "Explain L1 and L2 regularization.",
  "improved_answer": "Regularization adds a penalty term...",
  "next_difficulty": "medium"
}
```

---

# 13. Session-Level Analytics Summary

The analytics summary contains:

```text
session_id
total_questions
average_score
average_technical_accuracy
average_relevance
average_clarity
average_completeness
subtopic_performance
overall_performance
strong_areas
weak_areas
recommended_topics
learning_plan
```

This object is intended for:

* candidate performance dashboards
* topic/subtopic performance charts
* interview comparison dashboards
* learning recommendation views
* historical performance tracking

For active interviews, it represents the current session snapshot.

For completed interviews, it represents the complete session result.

---

# 14. Analytics Team Recommendation

For storage, the analytics team can conceptually maintain two datasets.

## Question-Level Dataset

One row per answered interview question.

Suggested columns:

```text
session_id
question_number
topic
subtopic
difficulty
technical_accuracy
relevance
clarity
completeness
overall_score
next_difficulty
```

Additional text fields such as feedback, strengths, weaknesses, and improved answers may also be stored if required.

## Session-Level Dataset

For final historical storage, one row per completed interview is recommended.

Suggested columns:

```text
session_id
total_questions
average_score
average_technical_accuracy
average_relevance
average_clarity
average_completeness
overall_performance
```

During an active interview, the `/analytics` response can also be treated as a temporary session snapshot.

`subtopic_performance` and `learning_plan` can be stored as JSON or normalized into separate tables depending on the analytics architecture.

---

# 15. Session Storage Architecture

Session storage is accessed through:

```text
backend/session_store.py
```

The FastAPI routes no longer manipulate a raw session dictionary directly.

Instead:

```text
FastAPI
   ↓
SessionStore
   ↓
InterviewSession
```

The current `SessionStore` supports:

```text
create
get
exists
delete
clear
```

This separates HTTP/API logic from session-storage logic and creates a clean replacement point for future persistent storage.

## Current Limitation

The current implementation is still in-memory.

Therefore:

* restarting the server clears active sessions
* sessions are not persisted across application restarts
* multiple independent server processes do not automatically share session state
* the implementation is suitable for development, testing, demos, and initial team integration

A future database-backed store could replace the current implementation without requiring the core interview intelligence logic to be rewritten.

Possible persistence targets include:

* PostgreSQL
* MongoDB
* another database selected by the project team

Database-specific logic should remain outside the Interview Intelligence core where possible.

---

# 16. LLM Modes

The project supports two execution modes.

## Mock Mode

Recommended for:

* development
* automated tests
* integration work
* frontend development
* analytics testing

Configure:

```env
LLM_MODE=mock
```

Mock mode avoids Gemini API calls and produces deterministic outputs.

It also allows other team members to develop against Part 2 without requiring Gemini credentials.

Mock mode should not require a Gemini API key or instantiate a Gemini client before entering the mock execution path.

## Real Gemini Mode

Used for real AI-generated interview behavior.

Configure:

```env
LLM_MODE=real
GEMINI_API_KEY=YOUR_KEY
GEMINI_MODEL=YOUR_MODEL
```

Never commit `.env` or API credentials to Git.

---

# 17. Gemini Reliability

Gemini calls use a shared retry helper for transient failures.

Handled transient status codes include:

```text
408
429
500
502
503
504
```

Connection failures and timeouts are also retried.

The current implementation uses limited retry attempts with exponential backoff and jitter.

Non-transient Gemini API errors are converted into controlled runtime errors.

Invalid structured Gemini responses are also converted into controlled runtime errors.

At the FastAPI boundary, relevant runtime failures are returned as HTTP `503` responses instead of allowing uncontrolled application crashes.

---

# 18. Multi-Agent Architecture

The Interview Intelligence module uses:

```text
InterviewSession
      ↓
InterviewOrchestrator
      ↓
 ┌──────────────────────┐
 │ InterviewerAgent     │
 │ EvaluatorAgent       │
 │ RecommendationAgent  │
 └──────────────────────┘
```

## InterviewerAgent

Generates interview questions using:

* topic
* difficulty
* previous questions
* resume context
* target role
* company context
* retrieved RAG context

The question generator avoids repeating previous questions where possible.

## EvaluatorAgent

Evaluates candidate answers and produces:

* technical accuracy
* relevance
* clarity
* completeness
* overall score
* strengths
* weaknesses
* constructive feedback
* improved answer

## RecommendationAgent

Produces personalized learning recommendations from subtopic-level performance.

The agents are coordinated through `InterviewOrchestrator` rather than being called independently by the API.

---

# 19. Important Ownership Boundary

AI/ML Part 2 consumes Part 1 outputs but should not duplicate Part 1 responsibilities.

## Part 1 Owns

```text
resume parsing
resume analysis
embeddings
vector database
RAG retrieval
company-specific information retrieval
candidate profile extraction
```

## Part 2 Owns

```text
interview orchestration
question delivery
answer evaluation
adaptive difficulty
structured scoring
feedback
improved answers
session history
performance summaries
learning recommendations
analytics export
Gemini reliability for Part 2 calls
```

This boundary should be maintained during integration to prevent duplicated pipelines.

---

# 20. API Error and Validation Behavior

Important API behavior currently includes:

```text
Invalid request schema              → 422
Invalid difficulty                  → 422
Invalid total_questions             → 422
Empty session_id/topic              → 422
Whitespace-only session_id/topic    → 422
Duplicate session                   → 400
Missing interview session           → 404
Question after completion           → 400
Part 2 runtime/LLM failure          → 503
```

Input normalization includes:

```text
session_id → strip leading/trailing whitespace
topic      → strip leading/trailing whitespace
```

`candidate_answer` is intentionally allowed to be empty because a no-answer response should be evaluated rather than rejected as a malformed API request.

If first-question generation fails during interview creation, the newly created session is removed from `SessionStore`.

This avoids leaving partially initialized sessions behind.

---

# 21. API State-Safety Rules

The API follows several important state-management rules.

## Pending Questions Must Not Be Skipped

Once a question has been generated, `/next` returns that question instead of silently generating another one.

Question progression happens through the normal answer-submission flow.

## Evaluation Context Remains Server-Side

The frontend submits the candidate answer only.

The question and expected concepts are maintained by the server.

## Read-Oriented Endpoints Should Not Advance the Interview

The following endpoints should not unexpectedly advance interview history:

```text
GET /
GET /health
GET /interview/{session_id}/next
GET /interview/{session_id}/report
GET /interview/{session_id}/analytics
```

The normal mutation/progression flow occurs through:

```text
POST /interview/start
POST /interview/answer
```

---

# 22. Automated Testing

Current test coverage includes:

* Gemini retry behavior
* mock question generation
* duplicate-question prevention
* empty/no-answer evaluation
* valid mock-answer evaluation
* adaptive difficulty
* learning recommendations
* interview session behavior
* session completion
* session history
* final reports
* Part 1 context acceptance
* integration schemas
* analytics exporter
* FastAPI endpoints
* analytics endpoint behavior
* missing-session handling
* API request validation
* invalid difficulty handling
* invalid interview length handling
* completed-interview edge cases
* health endpoint behavior
* SessionStore create/get behavior
* SessionStore duplicate protection
* SessionStore deletion
* SessionStore cleanup
* pending-question retrieval
* `/next` question-skip prevention
* retrieval of the post-answer pending question
* whitespace-only session ID rejection
* whitespace-only topic rejection
* session ID normalization
* topic normalization

Current verified result:

```text
51 passed
```

Run all relevant tests with:

```bash
python3 -m pytest ai_ml/interview_intelligence/tests backend/test_main.py backend/test_session_store.py -v
```

For normal automated testing, use:

```env
LLM_MODE=mock
```

The current environment may display two dependency deprecation warnings related to FastAPI/Starlette test dependencies.

These warnings do not represent failing project tests.

---

# 23. Real Gemini Smoke Testing

The Interview Intelligence pipeline has also been tested in real Gemini mode through an end-to-end smoke test.

The smoke test validated the flow:

```text
Part 1-style context
        ↓
Real Gemini question generation
        ↓
Candidate answer
        ↓
Real Gemini structured evaluation
        ↓
Deterministic difficulty adaptation
        ↓
Final performance summary
```

The test used candidate context related to Python/NLP, an ML Engineer role, recommendation systems, and retrieved embedding/ranking concepts.

Gemini generated a context-aware question.

An intentionally unrelated candidate answer was correctly identified as poor/irrelevant.

The deterministic adaptive engine reduced difficulty appropriately.

The final summary identified relevant weaknesses.

This confirms that mock-mode automated tests and real Gemini execution both exercise the intended architecture.

For normal development and CI-style testing, continue using mock mode to avoid unnecessary API usage and non-deterministic test behavior.

---

# 24. Recommended Team Integration Flow

The intended full-system flow is:

```text
Resume / Candidate Data
          ↓
AI/ML Part 1
          ↓
Resume Analysis + RAG
          ↓
InterviewContext
          ↓
FastAPI
          ↓
SessionStore
          ↓
AI/ML Part 2
Interview Intelligence
          ↓
Question-Level Evaluation
          ↓
Adaptive Interview
          ↓
Performance Report
          ↓
Analytics Exporter
          ↓
Backend / Persistent Storage
          ↓
Analytics + BI Dashboard
```

The cleanest integration point between modules is the structured schemas in:

```text
ai_ml/interview_intelligence/integration_schemas.py
```

These schemas should be treated as the contract between team components.

---

# 25. Integration Checklist

Before full team integration, verify:

* AI/ML Part 1 can populate the optional context fields.
* Backend/frontend uses a unique `session_id`.
* Leading/trailing whitespace in `session_id` and `topic` is safely normalized.
* Whitespace-only `session_id` and `topic` values are rejected.
* Frontend sends only the candidate answer for answer submission.
* Empty candidate answers remain valid interview responses.
* Difficulty values are `easy`, `medium`, or `hard`.
* Interview length is between 1 and 20 questions.
* `/next` returns the pending question instead of skipping ahead.
* `/report` can be used for performance-so-far or completed-interview reporting.
* `/analytics` can be used for active-session snapshots or completed-interview analytics.
* Development and integration environments use `LLM_MODE=mock` when real Gemini behavior is unnecessary.
* Real deployments provide Gemini configuration securely.
* Analytics consumes the exported question-level and session-level schemas.
* Database persistence is implemented outside the core Interview Intelligence logic.
* `.env` and credentials remain excluded from Git.
* `/health` can be used for lightweight service checks.
* The full automated test suite remains green before merging.

At the current checkpoint, the Interview Intelligence module is integration-ready with a verified **51-test passing baseline**.
