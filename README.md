# InterviewGPT

InterviewGPT is an AI-powered interview preparation platform that combines resume intelligence, retrieval-augmented generation (RAG), adaptive interviewing, structured answer evaluation, personalized feedback, learning recommendations, and analytics-ready outputs.

This repository currently contains the integrated AI/ML pipeline, FastAPI backend, automated tests, and a React/Vite demo frontend.

---

## System Overview

```text
Resume PDF
    |
    v
Resume Parsing & Analysis
    |
    v
Candidate Profile
    |
    v
BGE-M3 Embeddings
    |
    v
Candidate-Isolated Milvus Collection
    |
    v
Hybrid Dense + Sparse Retrieval
    |
    v
Reciprocal Rank Fusion (RRF)
    |
    v
Interview Context
    |
    v
Multi-Agent Interview Intelligence
    |
    +--> Interviewer Agent
    |
    +--> Evaluator Agent
    |
    +--> Recommendation Agent
    |
    v
Adaptive Interview
    |
    +--> Question Generation
    +--> Answer Evaluation
    +--> Difficulty Adaptation
    +--> Feedback
    +--> Improved Answer
    |
    v
Final Performance Report
    |
    v
Learning Recommendations
    |
    v
Analytics Export
```

---

## AI/ML Capabilities

### Part 1 — Resume Intelligence and RAG

The Part 1 pipeline provides:

- PDF resume parsing
- Gemini-based resume analysis
- structured candidate profile generation
- BGE-M3 dense and sparse embeddings
- Milvus vector storage
- candidate-specific collection isolation
- dense retrieval
- sparse retrieval
- Reciprocal Rank Fusion (RRF)
- resume-aware retrieval context
- resume question answering
- personalized question generation support

### Part 2 — Interview Intelligence

The Part 2 pipeline provides:

- AI-generated interview questions
- easy, medium, and hard difficulty levels
- adaptive difficulty progression
- multi-agent interview orchestration
- structured answer evaluation
- technical accuracy scoring
- relevance scoring
- clarity scoring
- completeness scoring
- overall scoring
- strengths and weaknesses
- detailed feedback
- improved answer generation
- interview history
- persistent interview sessions
- final performance reports
- subtopic-level performance analysis
- personalized learning recommendations
- analytics-ready exports

---

## Multi-Agent Architecture

The interview intelligence layer is orchestrated as:

```text
InterviewSession
    |
    v
InterviewOrchestrator
    |
    +--> InterviewerAgent
    |
    +--> EvaluatorAgent
    |
    +--> RecommendationAgent
```

The interviewer agent generates adaptive interview questions.

The evaluator agent evaluates candidate responses and produces structured multidimensional scores and feedback.

The recommendation agent contributes to the final learning and improvement recommendations.

---

## Repository Structure

```text
Major-Project/
|
+-- ai_ml/
|   |
|   +-- part1/
|   |   +-- resume/
|   |   +-- rag/
|   |   +-- llm/
|   |   +-- interview/
|   |   +-- tests/
|   |
|   +-- interview_intelligence/
|   |   +-- agents/
|   |   +-- tests/
|   |
|   +-- integration/
|
+-- backend/
|   +-- main.py
|   +-- session_store.py
|   +-- tests
|
+-- frontend/
|   +-- src/
|   +-- public/
|   +-- package.json
|
+-- data/
|
+-- docs/
|   +-- ANALYTICS_CONTRACT.md
|
+-- requirements.txt
+-- pytest.ini
+-- INTEGRATION_GUIDE.md
+-- AI_ML_PART2_NOTES.md
+-- README.md
```

---

# Running the AI/ML Demo

## 1. Clone the Repository

```bash
git clone <repository-url>
cd Major-Project
```

If you already have the repository, switch to the branch containing the integrated code.

---

## 2. Create a Python Virtual Environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

The AI/ML pipeline includes dependencies for FastAPI, Gemini integration, BGE-M3 embeddings, Milvus, resume processing, and testing.

---

## 4. Environment Configuration

Create a local `.env` file in the project root when using the real Gemini pipeline.

Example:

```text
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-3.1-flash-lite
```

Do not commit `.env`.

The project supports two LLM modes:

```text
LLM_MODE=mock
LLM_MODE=real
```

### Mock Mode

Mock mode is recommended for development, frontend work, automated testing, and demonstrations that do not require live Gemini calls.

### Real Mode

Real mode uses Gemini for the live AI workflow and requires valid Gemini configuration.

---

# Run the Backend

From the project root with the virtual environment activated:

## Mock Mode

```bash
LLM_MODE=mock python3 -m uvicorn backend.main:app --reload
```

## Real Gemini Mode

```bash
LLM_MODE=real python3 -m uvicorn backend.main:app --reload
```

The API runs by default on:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
GET /health
```

FastAPI documentation is available locally at:

```text
http://127.0.0.1:8000/docs
```

---

# Run the Demo Frontend

Open a second terminal.

```bash
cd frontend
npm install
npm run dev
```

Vite normally starts the frontend at:

```text
http://localhost:5173
```

The frontend communicates with the FastAPI backend running on port `8000`.

---

## Demo Flow

The sample frontend demonstrates the complete AI/ML workflow:

```text
Upload Resume
    |
    v
Resume Intelligence
    |
    v
Candidate Profile
    |
    v
RAG Context
    |
    v
AI Interview Question
    |
    v
Candidate Answer
    |
    v
AI Evaluation
    |
    +--> Technical Accuracy
    +--> Relevance
    +--> Clarity
    +--> Completeness
    +--> Overall Score
    |
    v
Strengths / Weaknesses
    |
    v
Feedback + Improved Answer
    |
    v
Adaptive Next Question
    |
    v
Final Performance Report
    |
    v
Personalized Learning Plan
    |
    v
Analytics Export
```

---

# API Endpoints

## Health

```text
GET /health
```

Checks whether the Interview Intelligence API is available and reports the current LLM mode.

## Start Interview From Resume

```text
POST /interview/start-from-resume
```

Multipart form fields:

```text
session_id
topic
resume
difficulty
total_questions
job_role             optional
company_context      optional
```

This endpoint runs the integrated Part 1 -> Part 2 workflow.

## Start Interview From Context

```text
POST /interview/start
```

Starts an interview from structured context without requiring resume upload.

## Submit Answer

```text
POST /interview/answer
```

Example:

```json
{
  "session_id": "candidate-session-001",
  "candidate_answer": "Candidate response..."
}
```

## Get Current / Next Question

```text
GET /interview/{session_id}/next
```

## Get Final Report

```text
GET /interview/{session_id}/report
```

## Get Analytics Export

```text
GET /interview/{session_id}/analytics
```

This endpoint exposes the AI/ML output intended for the analytics layer.

---

# Analytics Integration

The AI/ML layer exposes two primary analytics structures:

1. question-level performance records
2. interview-level summary analytics

The analytics team should consume these outputs rather than recomputing AI-generated evaluation scores or recommendations.

The complete contract is documented in:

```text
docs/ANALYTICS_CONTRACT.md
```

---

# Candidate Isolation

Resume embeddings are stored in candidate-specific Milvus collections.

This prevents retrieval context from one candidate from leaking into another candidate's interview.

The current demo uses:

```text
session_id -> candidate isolation key
```

This is sufficient for the current interview demo and session isolation.

For future longitudinal analytics where the same candidate may complete multiple interview sessions, introduce a stable:

```text
candidate_id
```

separately from:

```text
session_id
```

Recommended future relationship:

```text
Candidate
    |
    +-- candidate_id
           |
           +-- session_id_1
           +-- session_id_2
           +-- session_id_3
```

---

# Session Persistence

Interview sessions are persisted as JSON-backed session state.

The session storage layer supports:

- session creation
- session retrieval
- session updates
- pending-question persistence
- interview-history persistence
- session deletion
- restart recovery
- malformed-state protection
- atomic writes

The default persistent session directory is:

```text
data/sessions
```

It can be overridden using:

```text
INTERVIEWGPT_SESSION_DIR
```

Runtime session data should not be committed to Git.

---

# Testing

## Full Non-Live Regression Suite

From the project root:

```bash
LLM_MODE=mock python3 -m pytest \
  ai_ml/part1/tests \
  ai_ml/interview_intelligence/tests \
  ai_ml/integration \
  backend/test_main.py \
  backend/test_session_store.py \
  backend/test_session_persistence.py \
  -m "not live_gemini" \
  -v
```

At the AI/ML integration freeze point, this suite passed:

```text
92 passed
7 deselected
0 failures
```

---

## Controlled Real Gemini End-to-End Test

Real Gemini tests should be run deliberately rather than as part of the normal development test loop.

```bash
LLM_MODE=real python3 -m pytest \
  ai_ml/integration/test_real_resume_upload_api.py::test_real_resume_upload_full_interview_flow \
  -v -s
```

This validates the live flow:

```text
PDF Resume
  -> Gemini Resume Analysis
  -> BGE-M3 Embeddings
  -> Candidate-Isolated Milvus
  -> Hybrid Retrieval
  -> RRF
  -> Interview Context
  -> Adaptive Interview
  -> Gemini Evaluation
  -> Final Report
  -> Analytics
```

---

# Reliability and Safety Features

The integrated AI/ML layer includes:

- mock LLM mode
- Gemini retry handling
- transient API failure handling
- input validation
- resume file validation
- configurable resume upload size limits
- configurable interview question limits
- persistent sessions
- atomic session writes
- candidate-specific vector isolation
- pending-question recovery
- duplicate-session protection
- analytics schema validation
- automated regression coverage

---

# AI/ML and Analytics Ownership Boundary

## AI/ML Owns

- resume parsing and analysis
- candidate profile generation
- embeddings
- vector storage
- hybrid retrieval
- RRF
- resume-aware context
- interview question generation
- adaptive difficulty
- answer evaluation
- technical accuracy score
- relevance score
- clarity score
- completeness score
- overall score
- strengths
- weaknesses
- feedback
- improved answers
- final performance summaries
- subtopic performance
- learning recommendations

## Analytics Owns

- consuming AI/ML outputs
- candidate performance analytics
- aggregations
- KPI generation
- comparisons
- visualizations
- dashboards
- BI/reporting
- longitudinal analysis

Analytics should treat the AI/ML evaluation and recommendation outputs as upstream contract fields rather than redefine them independently.

---

# Development Branches

The project uses individual development branches for team ownership.

At the current integration stage:

```text
tanishka  -> AI/ML Part 1 development
arnav     -> integrated AI/ML Part 1 + Part 2 + demo frontend
samridhi  -> analytics development
garima    -> analytics/dashboard development
main      -> stable integrated project
```

Individual branches should remain available for development history and ownership.

Stable, tested integration checkpoints should be merged into `main`.

---

# Additional Documentation

Detailed AI/ML implementation and integration notes are available in:

```text
AI_ML_PART2_NOTES.md
INTEGRATION_GUIDE.md
ai_ml/part1/README.md
docs/ANALYTICS_CONTRACT.md
```

---

# Current AI/ML Status

```text
Resume Intelligence             Complete
Candidate Profile               Complete
BGE-M3 Embeddings               Complete
Milvus Vector Storage           Complete
Candidate Isolation             Complete
Hybrid Dense/Sparse Retrieval   Complete
RRF                             Complete
Part 1 -> Part 2 Integration    Complete
AI Interviewer                  Complete
Adaptive Difficulty             Complete
Answer Evaluation               Complete
Structured Scoring              Complete
Feedback                        Complete
Improved Answers                Complete
Session Persistence             Complete
Final Performance Report        Complete
Learning Recommendations        Complete
Analytics Export                Complete
FastAPI Integration             Complete
React Demo Frontend             Complete
Mock End-to-End Flow            Passed
Real Gemini End-to-End Flow     Passed
```

The AI/ML layer is considered frozen for analytics integration. Changes should now be driven by concrete integration requirements or bug fixes rather than additional feature expansion.
