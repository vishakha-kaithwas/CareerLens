# CareerLens — AI-Powered Career Gap Intelligence Platform

CareerLens is a portfolio-grade AI platform that analyzes the gap between a candidate's resume and target job requirements, providing explainable match justifications, prioritized skill dependencies, and practical improvement roadmaps.

## Architecture

- **Backend Framework**: FastAPI (modular application factory with versioned routers)
- **Settings**: Pydantic Settings (`pydantic-settings`) loading from `.env`
- **Document Processing**: PyMuPDF (`pymupdf`) for memory-efficient text and metadata extraction
- **Testing**: Pytest with `pytest-asyncio` and `httpx`

---

## Milestone 1: Project Foundation & Resume Extraction

Milestone 1 delivers the backend foundation, configuration management, health check endpoints, in-memory PDF extraction, and validation handling.

---

## Milestone 2: Resume Information Extraction & Job Description Parsing

Milestone 2 delivers deterministic NLP and rule-based parsing modules for resumes and job descriptions without relying on external LLM APIs:

1. **Resume Section Segmentation & Extraction**:
   - Parses extracted PDF text into structured sections: Contact Info, Summary, Technical Skills, Experience, Education, Projects, and Certifications.
   - Normalizes technical skills into canonical taxonomy names (e.g., `postgres` -> `PostgreSQL`, `k8s` -> `Kubernetes`, `py` -> `Python`).
   - Extracts candidate contact info using regex and spaCy NER while filtering out pagination artifacts.
   - Preserves `raw_text` for every entry for downstream evidence-based verification.
2. **Job Description Parsing**:
   - Accepts raw pasted job descriptions via `POST /api/v1/jobs/parse`.
   - Distinguishes **required mandatory skills** from **preferred / bonus skills**.
   - Extracts years of experience criteria, education degrees, tools & technologies, soft skills, and day-to-day responsibilities.
   - Preserves `raw_text` for transparency.

---

## Milestone 3: Intelligent Skill Matching & Semantic Similarity

Milestone 3 implements an explainable, multi-tiered matching engine that compares structured candidate qualifications against job requirements without using black-box LLMs:

### 1. Three-Tier Matching Strategies
1. **Exact Matching**: Identifies identical case-insensitive skill names (score = `1.0`).
2. **Normalized Taxonomy Matching**: Reuses the centralized taxonomy (`app.ml.skill_taxonomy`) to resolve aliases and abbreviations (e.g. `postgres` -> `PostgreSQL`, `k8s` -> `Kubernetes`, `js` -> `JavaScript`) (score = `1.0`).
3. **Semantic Similarity Matching**:
   - Uses Sentence Transformers (`all-MiniLM-L6-v2`) via a thread-safe singleton `EmbeddingEngine` on CPU.
   - Compares requirement embeddings against candidate resume skills, experience bullet points, and project descriptions.
   - Calculates **Cosine Similarity** between L2-normalized dense 384-dimensional vectors:
     $$\text{Cosine Similarity} = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
   - Matches are accepted when similarity exceeds the configurable threshold (`SEMANTIC_SIMILARITY_THRESHOLD = 0.65`).
   - **Distinct Technology Safety**: Hard guards prevent false positives between distinct technologies with similar embeddings (e.g. `Python` $\neq$ `PyTorch`, `Java` $\neq$ `JavaScript`, `SQL` $\neq$ `NoSQL`).

### 2. Evidence-Based Grounding
Every matched requirement retains:
- `matched_resume_skill`: The candidate skill or phrase that satisfied the requirement.
- `resume_evidence`: Verbatim contextual bullet or snippet from the resume.
- `job_evidence`: Verbatim requirement statement from the job posting.
- `similarity_score`: Score between 0.0 and 1.0.
- `match_method`: `exact`, `normalized`, `semantic`, or `none`.

---

## Milestone 4: Career Gap Analysis & Explainable Coverage Scoring

Milestone 4 consumes the matching intelligence from Milestone 3 and evaluates requirement proficiency depth, assigning transparent classifications and non-misleading coverage scores.

### 1. Requirement Classification Logic
Every job requirement is placed into exactly one evidence-grounded tier:
- **Matched** (Weight: `1.0`): Exact or normalized skill match supported by substantive contextual experience or project achievements.
- **Partially Demonstrated** (Weight: `0.5`):
  - Skill is listed as a standalone keyword in resume skills without contextual project/work implementation details.
  - Or, semantic similarity identified a related concept without verifying hands-on production proficiency.
- **Not Demonstrated** (Weight: `0.0`): No relevant evidence exists in the resume.

### 2. Explainable Coverage Scoring Formula
1. **Category Coverage (Required & Preferred)**:
   $$\text{Category Coverage} = \frac{(\text{Matched} \times 1.0) + (\text{Partial} \times 0.5) + (\text{Not Demonstrated} \times 0.0)}{\text{Total Category Requirements}} \times 100$$
2. **Overall Job Requirement Coverage**:
   $$\text{Overall Coverage} = (\text{Required Score} \times 0.80) + (\text{Preferred Score} \times 0.20)$$
   *(If no preferred requirements exist, Required Score represents 100% of the overall score. If no criteria exist at all, returns null).*
3. **Non-Misleading Disclosure**:
   Coverage score measures text evidence demonstration and is explicitly **not** labeled as hiring probability or ATS rank.

---

## Milestone 5: Skill Dependency Intelligence & Personalized Improvement Roadmap

Milestone 5 transforms career gap findings into an actionable, dependency-aware improvement roadmap. Rather than offering arbitrary skill checklists, the engine maps learning prerequisites using a directed acyclic graph (DAG) and recommends real-world portfolio deliverables.

### 1. Curated Skill Knowledge Base (`app.ml.skill_knowledge_base`)
The knowledge base maps technologies across domains:
- **Domains Covered**: Programming Languages, Backend Development, Databases, Machine Learning, AI & GenAI, Cloud & DevOps, Software Engineering Fundamentals.
- **Attributes per Skill**:
  - `prerequisites`: Required foundational technologies (e.g. `Python` $\rightarrow$ `FastAPI`, `Docker` $\rightarrow$ `Kubernetes`, `Linear Algebra` $\rightarrow$ `Machine Learning`).
  - `suggested_topics`: Concrete curriculum topics to learn.
  - `practical_projects`: Hands-on project deliverables with real-world scenarios and measurable acceptance criteria.
  - `estimated_duration_weeks` & `estimated_hours`: Realistic learning investment estimates.

### 2. Directed Acyclic Graph (DAG) & Topological Ordering (`app.ml.dependency_graph`)
- **Cycle Detection**: Depth-first search (DFS) with cycle detection guarantees graphs remain acyclic.
- **Unmet Prerequisite Traversal**: Recursively identifies all missing upstream foundations that the candidate does not possess.
- **Topological Sorting**: Sequences learning steps so that foundational dependencies are scheduled before advanced tools (e.g. learning `Docker` before `Kubernetes`).

### 3. Four-Tier Priority Scoring
Target learning steps are prioritized based on gap severity and role criticality:
1. `CRITICAL`: Unmet prerequisites for mandatory requirements.
2. `HIGH`: Missing mandatory requirements (`not_demonstrated`).
3. `MEDIUM`: Partially demonstrated requirements needing depth.
4. `LOW`: Preferred / nice-to-have job skills.

---

## Milestone 6: Evidence-Based Resume Improvement

Milestone 6 generates targeted, honest resume improvements tailored to a specific job description without using black-box LLMs or fabricating facts.

### 1. Bullet Analysis & Action Verb Transformation
- **Passive Verb Enhancement**: Replaces weak openers (`worked on`, `helped with`, `responsible for`) with strong engineering action verbs (`Engineered`, `Collaborated on`, `Developed`, `Implemented`).
- **Vague Qualifier Detection**: Detects ambiguous phrases (`various technologies`, `different tools`, `some bugs`) and prompts the candidate for specifics.

### 2. Zero-Hallucination Evidence Grounding Rules
- **No Invented Metrics**: Never generates synthetic percentages, dollar savings, or latency numbers.
- **Candidate Clarification Questions**: If a bullet lacks quantifiable results, the engine generates concrete inquiry questions for the candidate to provide truthful data.
- **Buried Skills Elevation**: Identifies technologies implemented in project descriptions (e.g. `Docker`) that were omitted from the primary technical skills section.
- **Truthful Alignment**: Connects existing project and work experience directly to matching job requirements with traceable source evidence.

---

## Milestone 7: Complete Frontend & Backend Integration

Milestone 7 delivers a modern, responsive React + TypeScript single-page application (SPA) with a dedicated intelligence dashboard, interactive timeline roadmap, bullet improvement workspace, and entity inspection.

### 1. Technology Architecture
- **Framework**: React 19 + TypeScript (bundled with Vite 8)
- **Styling**: Tailwind CSS v4 + Plus Jakarta Sans typography
- **Navigation**: React Router v7 (`/`, `/analyze`, `/dashboard`, `/roadmap`, `/improvement`, `/overview`)
- **Data Visualizations**: Recharts for dynamic requirement distribution
- **Icons**: Lucide React
- **HTTP Client**: Axios with centralized error formatting and type-safe backend schemas

### 2. Privacy & Memory Guarantees
- Sensitive resume text and personal information are kept purely in active React memory context (`WorkflowContext`).
- No candidate data or resume contents are persisted to `localStorage`, `sessionStorage`, or remote databases.
- A one-click "New Analysis" action immediately purges active workflow state from client memory.

---

## Getting Started

### 1. Backend Setup & Startup

```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m pytest -v
python -m uvicorn app.main:app --reload --port 8000
```

- Backend API: [http://localhost:8000](http://localhost:8000)
- OpenAPI Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend Setup & Startup

```bash
cd frontend
npm install
npm run build
npm run dev
```

- Frontend Web App: [http://localhost:5173](http://localhost:5173)

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health status and uptime diagnostics. |
| `POST` | `/api/v1/resumes/extract` | Uploads PDF resume and returns plain text and layout metadata in memory. |
| `POST` | `/api/v1/resumes/parse` | Uploads PDF resume and parses structured sections, entities, and normalized skills. |
| `POST` | `/api/v1/jobs/parse` | Accepts pasted job description text and extracts structured requirements. |
| `POST` | `/api/v1/matching/skills` | Compares parsed resume and job description using exact, normalized, and semantic matching with evidence retention. |
| `POST` | `/api/v1/analysis/gaps` | Generates complete career gap analysis, requirement classifications, and explainable coverage scoring. |
| `POST` | `/api/v1/roadmap/generate` | Generates a sequenced, dependency-aware improvement roadmap with project deliverables. |
| `POST` | `/api/v1/resume/improve` | Generates evidence-grounded resume improvements without fabricating metrics or facts. |
