# InterviewGPT

InterviewGPT is an AI-powered interview preparation system that uses Resume Analysis, Large Language Models (LLMs), and Retrieval-Augmented Generation (RAG) to provide personalized interview assistance.

---

## Project Overview

The system processes a candidate's resume and uses the extracted information to:

- Analyze the candidate's profile
- Create structured candidate information
- Generate dense and sparse embeddings
- Store resume information in Milvus
- Perform Hybrid Retrieval
- Combine retrieval results using Reciprocal Rank Fusion (RRF)
- Generate personalized interview questions
- Answer questions about the candidate's resume using Gemini

---

## Step-by-Step Pipeline

### Step 1: Resume Input

The user provides a candidate's resume in PDF format.

```text
Candidate Resume (PDF)
        ↓
Resume Processing Pipeline
```

The resume is stored inside:

```text
data/raw/
```

---

### Step 2: Resume Parsing

The PDF resume is processed using the resume parser.

The parser extracts the textual content from the PDF.

```text
PDF Resume
    ↓
PDF Parser
    ↓
Extracted Resume Text
```

The extracted text becomes the input for the next stage.

---

### Step 3: Resume Analysis

The extracted resume text is sent to Gemini for analysis.

The LLM identifies important candidate information and converts it into a structured profile.

The extracted information includes:

- Name
- Education
- Technical Skills
- Programming Languages
- Libraries and Tools
- Projects
- Experience
- Certifications
- Strengths

```text
Extracted Resume Text
        ↓
     Gemini LLM
        ↓
Structured Candidate Profile
```

The structured profile is saved as:

```text
data/processed/candidate_profile.json
```

---

### Step 4: Candidate Document Creation

The structured candidate profile is converted into a document suitable for the RAG pipeline.

```text
Structured Candidate Profile
        ↓
   Document Creation
        ↓
      RAG Document
```

This document contains the candidate's information in a format suitable for retrieval.

---

### Step 5: Text Chunking

The RAG document is divided into smaller chunks.

Chunking helps the retrieval system search for relevant information more efficiently.

```text
RAG Document
      ↓
 Text Chunking
      ↓
Multiple Resume Chunks
```

Each chunk represents a smaller piece of candidate information.

---

### Step 6: Dense and Sparse Embeddings

Each resume chunk is converted into two different representations.

#### Dense Embeddings

Dense embeddings capture the semantic meaning of the text.

They help retrieve information based on:

- Meaning
- Context
- Semantic similarity

#### Sparse Embeddings

Sparse embeddings focus on:

- Keywords
- Important terms
- Lexical similarity

```text
Resume Chunks
      ↓
Embedding Models
      ↓
┌─────────────────────┐
↓                     ↓
Dense Embeddings   Sparse Embeddings
```

---

### Step 7: Store Data in Milvus

The resume chunks and their embeddings are stored in Milvus.

Each stored record contains:

- Document ID
- Resume text
- Dense embedding
- Sparse embedding

```text
Resume Chunks
      ↓
Dense + Sparse Embeddings
      ↓
    Milvus Database
```

Milvus is used as the vector database for retrieval.

---

### Step 8: Hybrid Retrieval

When the user asks a question, the system performs two types of retrieval.

#### Dense Search

Dense search retrieves information based on semantic similarity.

#### Sparse Search

Sparse search retrieves information based on keyword similarity.

```text
User Query
    ↓
Query Processing
    ↓
┌─────────────────────┐
↓                     ↓
Dense Search       Sparse Search
↓                     ↓
Dense Results      Sparse Results
```

---

### Step 9: Reciprocal Rank Fusion

The results from dense and sparse retrieval are combined using Reciprocal Rank Fusion (RRF).

RRF combines the rankings from multiple retrieval systems to produce better results.

```text
Dense Search Results
        ↓
        │
        ├── Reciprocal Rank Fusion
        │
        ↓
Sparse Search Results
        ↓
Final Ranked Results
```

The final ranked results contain the most relevant resume information.

---

### Step 10: Resume Question Answering

The system can answer questions related to the candidate's resume.

```text
User Question
      ↓
Hybrid Retrieval
      ↓
Relevant Resume Context
      ↓
     Gemini LLM
      ↓
Generated Answer
```

Example questions include:

- What programming languages does the candidate know?
- What projects has the candidate worked on?
- What are the candidate's technical skills?

---

### Step 11: Interview Question Generation

The system generates personalized interview questions using the candidate's resume information.

Supported interview types include:

- Technical
- HR
- Behavioral

```text
Candidate Information
        ↓
   Hybrid Retrieval
        ↓
Relevant Resume Context
        ↓
      Gemini LLM
        ↓
Personalized Interview Questions
```

This ensures that the generated questions are relevant to the candidate's actual profile.

---

## Hybrid RAG Architecture

The complete Part 1 pipeline can be represented as:

```text
                    PDF RESUME
                        ↓
                 TEXT EXTRACTION
                        ↓
                  RESUME ANALYSIS
                        ↓
             STRUCTURED CANDIDATE PROFILE
                        ↓
                RAG DOCUMENT CREATION
                        ↓
                   TEXT CHUNKING
                        ↓
           ┌────────────┴────────────┐
           ↓                         ↓
    DENSE EMBEDDINGS          SPARSE EMBEDDINGS
           ↓                         ↓
           └────────────┬────────────┘
                        ↓
                 MILVUS DATABASE
                        ↓
                    USER QUERY
                        ↓
                QUERY EMBEDDINGS
                        ↓
           ┌────────────┴────────────┐
           ↓                         ↓
      DENSE SEARCH              SPARSE SEARCH
           ↓                         ↓
           └────────────┬────────────┘
                        ↓
           RECIPROCAL RANK FUSION
                        ↓
             RELEVANT RESUME CONTEXT
                        ↓
                   GEMINI LLM
                        ↓
           ┌────────────┴────────────┐
           ↓                         ↓
   INTERVIEW QUESTIONS          RESUME ANSWERS
```

## Project Structure

```text
interviewgpt/
│
├── app/
│   │
│   ├── config/
│   │
│   ├── interview/
│   │   ├── __init__.py
│   │   └── question_generator.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   └── gemini_client.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── documents.py
│   │   ├── embeddings.py
│   │   ├── milvus_store.py
│   │   ├── qa.py
│   │   └── retriever.py
│   │
│   ├── resume/
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   └── parser.py
│   │
│   └── schemas/
│
├── data/
│   │
│   ├── raw/
│   │   └── Tanishka latest.pdf
│   │
│   ├── processed/
│   │   └── candidate_profile.json
│   │
│   └── milvus.db
│
├── tests/
│   │
│   ├── interview/
│   │   └── test_question_generator.py
│   │
│   ├── llm/
│   │   └── test_gemini.py
│   │
│   ├── rag/
│   │   ├── test_chunker.py
│   │   ├── test_collection.py
│   │   ├── test_documents.py
│   │   ├── test_embeddings.py
│   │   ├── test_hybrid_retrieval.py
│   │   ├── test_insert.py
│   │   ├── test_milvus.py
│   │   ├── test_resume_qa.py
│   │   ├── test_retrieval.py
│   │   ├── test_rrf_retrieval.py
│   │   └── test_sparse_retrieval.py
│   │
│   └── resume/
│       ├── test_resume_analyzer.py
│       └── test_resume_parser.py
│
├── .env
├── .gitignore
├── main.py
└── README.md
```
## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/Tanishka1223/InterviewGPT-Part1.git
```

Move into the project directory:

```bash
cd InterviewGPT-Part1
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

#### Windows

```bash
venv\Scripts\activate
```

---

### 3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the root directory.

Add your Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

---

### 5. Add a Resume

Place the candidate's PDF resume inside:

```text
data/raw/
```

Currently, the resume path is configured inside `main.py`:

```python
pdf_path = "data/raw/Tanishka latest.pdf"
```

Make sure the filename matches the path configured in `main.py`.

---

### 6. Run the Application

Run:

```bash
python main.py
```

The application will display:

```text
1. Process Resume
2. Generate Interview Questions
3. Ask Resume Question
4. Exit
```

---

### 7. Process the Resume

First, select:

```text
1
```

This will:

- Extract text from the resume
- Analyze the resume using Gemini
- Create a RAG document
- Chunk the document
- Generate dense and sparse embeddings
- Store the information in Milvus

After processing is complete, the resume information is ready for retrieval.

---

### 8. Generate Interview Questions

Select:

```text
2
```

Choose an interview type:

- Technical
- HR
- Behavioral

Then enter the number of questions.

The system generates personalized interview questions based on the candidate's resume.

---

### 9. Ask Questions About the Resume

Select:

```text
3
```

Enter a question related to the candidate's resume.

Example:

```text
What programming languages does the candidate know?
```

The system retrieves relevant information using Hybrid RAG and generates an answer using Gemini.