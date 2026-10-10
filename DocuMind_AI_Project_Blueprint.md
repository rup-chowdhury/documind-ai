# Project Blueprint: DocuMind AI

> Production-oriented document intelligence platform · 6-week MVP · Full-stack + AI Engineering

Your project will be **DocuMind AI**, a web application that lets users upload documents, ask questions about their contents, receive evidence-backed answers with citations, and manage their documents securely.

The objective is to demonstrate two capabilities in one portfolio project:

- **Software Engineering:** design, implement, test, secure, deploy, and maintain a complete web application.
- **AI Engineering:** build a document-processing and retrieval-augmented generation (RAG) pipeline, evaluate its quality, and optimize its reliability, latency, and cost.

Given your existing Python, ML, and data-mining experience, this project moves you toward applied AI engineering without making the frontend and backend secondary concerns.

## 1. Concrete product definition

### The problem

Professionals and students often have to search through multiple PDFs to find specific information. Traditional keyword search struggles when a question uses different wording from the source document, while general-purpose chatbots may generate answers unsupported by the documents.

### The proposed solution

A user uploads documents to a private workspace and asks questions such as:

- "What methodology did this research paper use?"
- "Compare the limitations of these two papers."
- "What are the main requirements in this specification?"
- "Which page supports this answer?"

DocuMind AI retrieves relevant passages from the user's documents and generates an answer grounded in those passages.

**Core product rule:** If the documents do not contain enough evidence, the application should say so rather than confidently inventing an answer.

### Target users

- University students and researchers
- Software engineers working with technical documentation
- Small teams managing internal knowledge

For the MVP, prioritize research papers and technical PDFs. This narrows document parsing, testing, and evaluation to a manageable scope.

## 2. MVP scope: what you will actually build

Keep the initial release focused. Six weeks is enough for a well-engineered MVP if you limit the number of features and use managed infrastructure where practical.

### Must-have features

- User registration, login, logout
- Private document library
- PDF upload, validation, and deletion
- Asynchronous document processing with status tracking
- AI question-answering over uploaded documents
- Source citations with page numbers and supporting excerpts
- Document search and chat history
- Responsive dashboard and clear error states

### If time permits

- Compare two or more documents
- Download answers as Markdown
- Reranking for improved retrieval
- Basic usage and token-cost dashboard

### Out of scope for six weeks

- Autonomous multi-agent workflows
- Training a foundation model from scratch
- OCR for every possible scanned-document format
- Microservices and Kubernetes from day one
- Enterprise SSO, billing, and complex team administration

### User journey

1. **Register and log in**
2. **Upload a PDF** — validate the file and create a processing job.
3. **Process the document** — extract text, chunk, embed, and index.
4. **Ask a question** — retrieve passages and generate an answer.
5. **Inspect the evidence** — review the answer, source document, page number, and excerpt.

## 3. Technology stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | Next.js + TypeScript | Production-style web UI and type safety |
| UI styling | Tailwind CSS | Rapid, consistent interface development |
| Backend | Python + FastAPI | Typed APIs and straightforward AI integration |
| Validation | Pydantic | Request and response validation |
| Database | PostgreSQL | Users, documents, chats, jobs, and metadata |
| Vector search | pgvector | Store and retrieve embeddings in PostgreSQL |
| File storage | S3-compatible object storage | Store original PDFs separately from metadata |
| Background tasks | Redis + Celery | Process uploads without blocking API requests |
| AI models | Embedding model + LLM API | Semantic retrieval and answer generation |
| Testing | pytest + Playwright | Backend tests and browser-level workflows |
| Containers | Docker + Docker Compose | Reproducible local development |
| CI/CD | GitHub Actions | Automated tests and deployment |
| Deployment | Managed cloud app hosting + managed PostgreSQL | Reduce infrastructure overhead during the MVP |
| Monitoring | Structured logs + error tracking | Diagnose production failures |

**Important design choice:** start with a modular monolith. Keep document processing and AI orchestration in separate Python modules, and run the worker as a separate process. You can scale the worker independently without the operational cost of a microservice architecture.

## 4. System architecture

### Main components

- **Next.js frontend:** document library, upload progress, chat, citations.
- **FastAPI application:** authentication, authorization, document APIs, chat APIs.
- **PostgreSQL + pgvector:** relational data, chat history, and vector index.
- **Object storage:** original PDF files with private access.
- **Redis + background worker:** job queue, retries, PDF extraction, chunking, and embedding generation.
- **AI retrieval and generation pipeline:** query embedding, vector retrieval, context assembly, LLM, and citation validation.

### Two independent execution flows

**A. Document ingestion**

The user uploads a PDF. The API validates it, saves it to private object storage, creates a document record, and enqueues a processing job. The worker extracts and indexes the content asynchronously. The UI polls the document status until it becomes `ready` or `failed`.

**B. Question answering**

The API checks user permissions, retrieves relevant chunks from pgvector, calls the generation model, validates citation references, and stores the response and citations. The frontend renders the answer with links to the relevant source pages.

This separation prevents a slow embedding or LLM request from blocking document uploads and other API requests.

## 5. Database schema

Use PostgreSQL for both relational records and vector search. This avoids managing a separate vector database during the six-week build.

**Recommended initial schema: 7 core tables.**

| Table | Important columns | Purpose |
|---|---|---|
| `users` | `id`, `email`, `password_hash`, `created_at` | Accounts and identity |
| `documents` | `id`, `user_id`, `filename`, `storage_key`, `status`, `file_size`, `checksum`, `created_at` | Document metadata and ownership |
| `processing_jobs` | `id`, `document_id`, `status`, `attempts`, `error_code`, `started_at`, `completed_at` | Ingestion job tracking |
| `document_chunks` | `id`, `document_id`, `chunk_index`, `page_number`, `content`, `embedding` | Text chunks and vector representations |
| `conversations` | `id`, `user_id`, `title`, `created_at` | Chat sessions |
| `messages` | `id`, `conversation_id`, `role`, `content`, `created_at` | User questions and AI responses |
| `citations` | `id`, `message_id`, `chunk_id`, `relevance_score` | Links between generated answers and source passages |

### Relationships

- `users` 1 → many `documents`
- `documents` 1 → many `document_chunks`
- `users` 1 → many `conversations`
- `conversations` 1 → many `messages`
- Each AI message can have multiple citations linked to retrieved chunks.

### Essential database constraints

- Use UUID primary keys and foreign keys.
- Add indexes on `documents.user_id`, `document_chunks.document_id`, and conversation/message relationships.
- Use a unique constraint on `(document_id, chunk_index)`.
- Store embeddings using the vector dimension required by your chosen embedding model.
- Use a vector index when the dataset and query volume justify it; compare approximate search against exact search during evaluation.
- Enforce ownership checks in backend queries. A user must never retrieve another user's documents, chunks, or conversations.
- Store only object-storage keys in PostgreSQL, not large PDF binaries.
- Track ingestion state and errors so failed jobs can be retried safely.

For a clean implementation, also maintain migrations using Alembic. Do not rely on automatic table creation in production.

## 6. AI engineering pipeline

This is the part that differentiates the project from a conventional CRUD application.

### Pipeline A — Document ingestion

1. **Validate and extract:** check file type, size, and PDF validity. Extract text while preserving page boundaries.
2. **Clean and chunk:** normalize extracted text and split it into overlapping chunks. Retain document ID, page number, and chunk index.
3. **Generate embeddings:** encode each chunk with a selected embedding model. Batch requests and handle rate limits.
4. **Store and index:** persist chunk text, page metadata, and embedding vectors in PostgreSQL/pgvector.
5. **Verify completion:** mark the document ready only after indexing succeeds. Record failures and allow controlled retries.

### Pipeline B — Question answering (RAG)

1. **Receive the question:** validate the request and verify access to the selected documents.
2. **Retrieve relevant chunks:** embed the query and perform similarity search over authorized chunks. Start with top-k = 5.
3. **Assemble context:** provide retrieved passages and source identifiers to the model within a defined context budget.
4. **Generate a grounded answer:** instruct the LLM to answer only from the supplied evidence and abstain when evidence is insufficient.
5. **Validate citations:** check that every cited chunk exists in the retrieved set, belongs to an authorized document, and has a valid page reference.
6. **Persist and measure:** save the answer and citations. Record latency, token usage, errors, and evaluation signals.

### AI models and initial configuration

| Component | Initial choice |
|---|---|
| PDF extraction | PyMuPDF |
| Embeddings | A compact sentence-transformer model or a hosted embedding API |
| Vector search | pgvector cosine similarity |
| Generation | A hosted LLM API with structured output |
| Retrieval | Top-5 chunks, followed by prompt-based context assembly |
| Chunking | Start around 500–800 tokens with 75–100 tokens of overlap |
| Evaluation | A versioned question-answer dataset plus automated retrieval and answer metrics |

These are starting configurations, not universal optimal values. Evaluate at least two chunk sizes or retrieval configurations rather than assuming the initial settings are best.

### Make the AI measurable

Create an evaluation set of around 50–100 questions from representative PDFs. Include answerable questions, questions requiring multiple passages, and unanswerable questions.

For each question, record:

- Expected answer or key facts
- Supporting document and page
- Relevant source passages
- Whether the system should abstain

Compare at least two retrieval configurations and preserve the results in your repository. For answer quality, combine automated checks with manual review of a representative sample.

## 7. Six-week implementation roadmap

**Assumption:** approximately 15–25 hours per week. This is an aggressive MVP schedule, so avoid adding optional features until the acceptance criteria for the core system pass.

### Week 1 — Requirements, architecture and foundation

- Write user stories and acceptance criteria.
- Create the Git repository, frontend and FastAPI skeleton.
- Design the ER diagram and PostgreSQL schema.
- Configure Docker Compose, environment variables and CI checks.

**Deliverable:** running application skeleton, schema migrations, and architecture diagram.

### Week 2 — Core full-stack application

- Implement registration, login and authorization.
- Build document library and upload interface.
- Implement private file storage and document metadata.
- Add file validation, deletion and processing-status UI.

**Deliverable:** a user can securely upload, list, and delete their own PDFs.

### Week 3 — Document ingestion and vector search

- Implement the Redis-backed task queue and worker.
- Extract text and page metadata using PyMuPDF.
- Implement chunking and embedding generation.
- Store vectors in pgvector and handle retries.

**Deliverable:** uploaded PDFs become searchable, with observable processing states.

### Week 4 — RAG and citation-backed chat

- Implement semantic retrieval and context assembly.
- Integrate the generation model.
- Add citation references and page-level source links.
- Persist conversations, messages, and citations.

**Deliverable:** a user can ask document-specific questions and inspect their sources.

### Week 5 — Evaluation, testing and hardening

- Create the 50–100-question evaluation set.
- Measure retrieval quality and answer groundedness.
- Add unit, integration, and end-to-end tests.
- Test authorization boundaries, retries, and malformed files.

**Deliverable:** an evaluation report, repeatable test suite, and documented failure handling.

### Week 6 — Cloud deployment and portfolio release

- Deploy frontend, API, and worker with managed services.
- Configure production secrets, migrations, and storage access.
- Add CI/CD, health checks, logs, and basic monitoring.
- Run acceptance tests and document the system.

**Deliverable:** a live demo, public code repository, README, architecture diagram, and measured results.

### Suggested daily workflow

- **First 10–15 minutes:** select a small task and define its completion criteria.
- **Main development block:** implement one vertical slice from UI to API to database or AI pipeline.
- **Final 15 minutes:** run tests, review the diff, and update the issue or README.
- **Every week:** deploy or demonstrate the latest working version rather than leaving integration until week six.

## 8. Measurable acceptance criteria

These are proposed project targets, not guaranteed results. Record the actual performance from your test environment and document any target you cannot meet.

| Area | Acceptance criterion |
|---|---|
| Functional completeness | A user can register, upload a PDF, ask a question, inspect citations, and delete the document without manual database operations. |
| Authentication | All protected endpoints reject unauthenticated requests. |
| Data isolation | Automated tests confirm that one user cannot access another user's documents, chunks, conversations, or citations. |
| Upload validation | Reject unsupported file types, oversized files, and invalid PDFs with actionable error messages. |
| Processing reliability | A simulated worker failure can be retried without duplicate chunks or inconsistent document state. |
| Retrieval quality | Recall@5 ≥ 0.85 on the labelled retrieval test set. |
| Answer quality | At least 85% of a manually reviewed, representative set of answerable questions are judged sufficiently supported by the cited evidence. |
| Abstention | At least 90% of a separate set of unanswerable questions receive an appropriate abstention rather than an unsupported substantive answer. |
| Citation integrity | 100% of returned citations resolve to existing retrieved chunks with correct document and page references. |
| API reliability | Core API unit and integration tests pass in CI; no known critical authorization failures remain. |
| Latency | On a documented test environment, target p95 retrieval-only latency below 1 second for a small test corpus, excluding embedding and LLM generation. |
| CI/CD | A successful main-branch pipeline runs tests and deploys the application to the configured environment. |
| Documentation | README includes setup, environment variables, migrations, deployment instructions, API documentation, architecture, and AI evaluation results. |

**How to interpret the AI targets:** Recall@5 measures whether relevant evidence appears among the five retrieved chunks. Answer groundedness should be judged against the source documents, not merely by whether the answer sounds plausible. Report the sample size and methodology alongside every percentage.

For latency, measure retrieval separately from the external LLM call. Hosted model latency depends on the provider, model, region, and response length, so avoid promising a fixed end-to-end response time before benchmarking.

## 9. Cloud deployment and CI/CD

Use the simplest managed cloud environment you can deploy to reliably. Since you're studying in Sweden, a European cloud region is a reasonable default for latency and data-residency planning, but it is not a substitute for reviewing the provider's data-processing terms.

### Deployment architecture

1. **GitHub repository:** feature branches, pull requests, and code review.
2. **GitHub Actions CI/CD:** lint, unit tests, integration tests, and build.
3. **Frontend hosting:** deploy the Next.js application.
4. **Backend hosting:** deploy FastAPI and worker processes.
5. **Managed services:** PostgreSQL/pgvector, Redis, object storage, and LLM API.

### Deployment checklist

- Store secrets in the hosting provider's secret manager or environment configuration, never in Git.
- Run database migrations as a controlled deployment step.
- Configure HTTPS, CORS, request-size limits, health checks, and database connection limits.
- Restrict object-storage access and use short-lived signed URLs when needed.
- Add timeouts, retry limits, and exponential backoff for external AI calls.
- Log request IDs, job IDs, model versions, latency, and token usage. Avoid logging passwords, API keys, or full private document contents.
- Configure a spending limit or alert for model usage and cloud resources.
- Verify the deployed application through an end-to-end smoke test.

Do not deploy PostgreSQL, Redis, and the worker on an exposed public interface just to simplify setup. Use private networking or the managed provider's recommended secure connection mechanism.

## 10. Suggested repository structure

```text
documind-ai/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── tests/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── document_processing/
│   │   ├── ai/
│   │   │   ├── embeddings.py
│   │   │   ├── retrieval.py
│   │   │   ├── generation.py
│   │   │   └── evaluation.py
│   │   └── workers/
│   ├── migrations/
│   └── tests/
├── evaluation/
│   ├── datasets/
│   ├── run_evaluation.py
│   └── reports/
├── infrastructure/
│   ├── docker/
│   └── deployment/
├── .github/
│   └── workflows/
├── docker-compose.yml
├── .env.example
└── README.md
```

Keep your AI logic independent of FastAPI route handlers. That makes it easier to test retrieval, swap models, run offline evaluations, and reuse the pipeline from background workers.

## 11. What will make this portfolio project stand out?

Many applicants can demonstrate an LLM chat interface. Your advantage will come from the engineering evidence behind it.

Aim to publish these five artifacts:

1. **Architecture decision records (ADRs):** explain why you chose pgvector, a background queue, and a modular monolith.
2. **AI evaluation report:** compare retrieval settings, show groundedness results, document failures, and explain limitations.
3. **Automated test suite:** include API tests, data-isolation tests, ingestion failure tests, and a browser-level happy path.
4. **Deployment pipeline:** show a successful automated build, test, and release.
5. **Technical demonstration:** upload documents, ask questions, open citations, demonstrate an unanswerable question, and show how failures are handled.

Also include a short section on known limitations. For example, text extraction may fail on scanned PDFs, semantically similar passages can still be irrelevant, and citations alone do not guarantee factual correctness.

## 12. Final recommendation

Your six-week priority order should be:

1. A reliable full-stack application with secure user isolation.
2. A repeatable document-ingestion pipeline.
3. Evidence-backed RAG with measurable quality.
4. Automated testing and robust error handling.
5. Cloud deployment, CI/CD, and clear technical documentation.

Do not sacrifice security, testing, or evaluation to add advanced AI features. A smaller system that is demonstrably reliable is a stronger portfolio project than a feature-rich prototype with no quality measurements.

**Confidence: 97%** — the architecture and schedule are appropriate for a focused six-week MVP. The main uncertainty is the time required to tune retrieval and answer quality, which depends on the selected models, document corpus, and available development hours.
