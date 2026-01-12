# Decision Calm Engine - Architecture

**Version:** 0.1.0 (MVP)
**Last Updated:** 2024-01-12

## 🎯 Mission

Enable users to make **calmer, better decisions** in 60 seconds through a multi-agent AI system that:
- Analyzes decision context without bias
- Presents options with consequences, not commands
- Suggests calming actions based on emotional state
- Respects user autonomy completely

**This is NOT**: Medical advice, therapy, crisis intervention, or diagnosis.

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │────────▶│   Next.js    │────────▶│   FastAPI   │
│   (User)    │◀────────│  Frontend    │◀────────│   Backend   │
└─────────────┘         └──────────────┘         └──────┬──────┘
                                                         │
                                                         │
                ┌────────────────────────────────────────┴──────────┐
                │                                                   │
                ▼                                                   ▼
        ┌───────────────┐                                 ┌─────────────┐
        │   Postgres    │                                 │   OpenAI    │
        │  + pgvector   │                                 │     API     │
        └───────────────┘                                 └─────────────┘
```

### Tech Stack

| Layer          | Technology                     | Version  |
|----------------|--------------------------------|----------|
| Frontend       | Next.js (App Router)           | 14.1     |
| Backend        | FastAPI                        | 0.109+   |
| Database       | PostgreSQL + pgvector          | 16       |
| AI Provider    | OpenAI (GPT-4o-mini)           | Latest   |
| Orchestration  | Custom (inspired by LangGraph) | -        |
| Infrastructure | Docker Compose                 | 3.9      |
| Language       | TypeScript (FE), Python (BE)   | TS5, Py3.11 |

---

## 📊 Multi-Agent System

### Agent Graph

```
User Input (3 Questions)
        ↓
┌───────────────────────┐
│   Intake Agent        │ → Normalize & structure input
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│   Context Agent       │ → Check if clarification needed (0-2 questions)
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│   Calmness Agent      │ → Generate "Calm Step" based on stress (1-10)
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│   Options Agent       │ → Generate 2-4 options + consequences + risks
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│   Safety Agent        │ → Validate content, block harmful patterns
└───────────┬───────────┘
            ↓
    Decision Brief
```

### Agent Responsibilities

| Agent            | Input                          | Output                                | Temperature |
|------------------|--------------------------------|---------------------------------------|-------------|
| **Intake**       | Raw user text                  | Structured JSON (decision, options)   | 0.3         |
| **Context**      | Structured input               | 0-2 clarifying questions (if needed)  | 0.3         |
| **Calmness**     | Context + stress level         | Calm step (breathing, break, etc.)    | 0.7         |
| **Options**      | Context + constraints          | 2-4 options + consequences + risks    | 0.7         |
| **Safety**       | All content                    | Safety validation + tone check        | 0.2         |

### Safety Rules

1. **Content Blocking**:
   - Self-harm keywords → Block + redirect to crisis resources
   - Medical diagnoses → Block with disclaimer
   - Authoritarian commands → Remove/rewrite

2. **Tone Validation**:
   - Reject: "you must", "you should", "do this now"
   - Accept: "you could consider", "one option is", "you might"

3. **Disclaimers**:
   - Always present on every Decision Brief
   - Crisis hotline numbers in footer

---

## 🗄️ Database Schema

### `decision_sessions` Table

```sql
CREATE TABLE decision_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- User (anonymous tracking)
    user_id VARCHAR(255),

    -- Input
    context TEXT NOT NULL,
    options TEXT NOT NULL,
    stress_level INTEGER NOT NULL CHECK (stress_level BETWEEN 1 AND 10),

    -- Output
    decision_brief JSONB,

    -- Metadata
    processing_time_seconds FLOAT,
    tags JSONB DEFAULT '[]',

    -- Vector search (1536 dimensions = text-embedding-3-small)
    embedding vector(1536),

    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Vector similarity index (IVFFlat for speed)
CREATE INDEX idx_embedding ON decision_sessions
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Vector Search

**Purpose**: Find similar past decisions for personalization.

**Flow**:
1. Embed user's context + options → 1536-dim vector
2. Store in `embedding` column
3. On future sessions, retrieve top-3 similar past decisions
4. Use as context for agents (optional enhancement)

**Distance Metric**: Cosine similarity (via pgvector)

---

## 🔄 Data Flow

### 1. Create Decision Session

```
POST /v1/decision/sessions
{
  "context": "Should I change jobs?",
  "options": "Stay, Leave, Negotiate",
  "stress_level": 7
}
```

**Backend Flow**:
1. Validate input (Pydantic)
2. Pass to `DecisionOrchestrator`
3. Orchestrator runs 5 agents sequentially
4. Assemble `DecisionBrief`
5. Store in Postgres
6. Generate embedding (async)
7. Return Decision Brief

**Response**:
```json
{
  "id": "uuid",
  "created_at": "2024-01-12T10:00:00Z",
  "output": {
    "options": [...],
    "calm_step": {...},
    "control_question": "...",
    "next_check_in": {...},
    "disclaimer": "..."
  }
}
```

### 2. Retrieve Session

```
GET /v1/decision/sessions/{id}
```

Fetch from Postgres, return full session + Decision Brief.

### 3. List Sessions

```
GET /v1/decision/sessions?user_id=abc&page=1&page_size=20
```

Paginated list of user's past sessions.

---

## 🌐 Frontend Architecture

### Pages (Next.js App Router)

| Route              | Component         | Purpose                          |
|--------------------|-------------------|----------------------------------|
| `/`                | `page.tsx`        | Landing + 3-question form        |
| `/session/[id]`    | `page.tsx`        | Decision Brief detail view       |
| `/history`         | `page.tsx`        | List of past sessions            |

### Components

- **DecisionForm**: 3-question form with validation
- **DecisionBrief**: Display options, calm step, control question
- **HistoryList**: List past sessions with previews

### State Management

- **Local State**: React `useState` for forms
- **API Client**: Centralized in `lib/api.ts`
- **No global state library needed for MVP**

---

## 🚀 Deployment

### Docker Compose (Local Dev)

```bash
docker compose --profile dev up --build
```

**Services**:
- `postgres`: PostgreSQL 16 + pgvector
- `api`: FastAPI backend
- `web`: Next.js frontend

**Profiles**:
- `dev`: Development mode (hot reload)
- `prod`: Production mode (optimized builds)
- `observability`: Adds metrics/tracing (optional)

### Environment Variables

See `.env.example` for full list. **Required**:
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `NEXT_PUBLIC_API_URL`

### Migrations

```bash
# Apply migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

---

## 🧪 Testing Strategy

### Backend

| Type          | Tool    | Coverage      |
|---------------|---------|---------------|
| Unit          | pytest  | Agents, utils |
| Integration   | pytest  | API endpoints |
| Contract      | OpenAPI | Schema tests  |

**Run Tests**:
```bash
cd services/api
pytest --cov=src
```

### Frontend

| Type          | Tool       | Coverage           |
|---------------|------------|--------------------|
| E2E           | Playwright | Full user flows    |
| Unit          | Vitest     | Components (future)|

**Run E2E**:
```bash
cd apps/web
npm run test:e2e
```

### CI/CD

GitHub Actions runs on every push:
1. Lint (ruff, eslint)
2. Type check (mypy, tsc)
3. Unit tests
4. Docker builds

---

## 🔐 Security & Privacy

### Data Protection

- **No PII required**: Anonymous user tracking (optional `user_id`)
- **No session cookies**: Stateless API
- **HTTPS only in production**

### API Security

- **Input validation**: Pydantic schemas
- **Rate limiting**: Optional (via Redis)
- **CORS**: Configured origins only
- **SQL injection protection**: SQLAlchemy ORM

### Content Safety

- **Keyword blocking**: Dangerous content filtered
- **OpenAI moderation**: Can add moderation API (future)
- **Disclaimers**: Always visible

---

## 📈 Observability (Optional)

### Logging

**Format**: Structured JSON (via `structlog`)

**Fields**:
- `timestamp`, `level`, `message`
- `agent_name`, `session_id`, `duration_ms`
- `error`, `stack_trace` (on errors)

**Output**: stdout (captured by Docker logs)

### Metrics (Future)

- Request latency (p50, p95, p99)
- Agent processing time
- Error rates
- OpenAI token usage

**Tools**: Prometheus + Grafana

---

## 🛣️ Roadmap (Post-MVP)

### Phase 2: Enhanced Personalization
- Use vector search for contextual recommendations
- Pattern detection across user's history
- "You've faced similar decisions before" insights

### Phase 3: Multimodal Inputs
- Voice input → transcription → processing
- Image upload → OCR → context extraction
- Support for non-text decision artifacts

### Phase 4: Collaboration
- Share Decision Briefs with trusted advisors
- Anonymous peer feedback (optional)
- Export decisions to PDF/markdown

### Phase 5: Advanced Safety
- OpenAI Moderation API integration
- Custom fine-tuned safety classifier
- Real-time crisis detection with escalation

---

## 🤝 Contributing

### Code Standards

- **Python**: Black, Ruff, MyPy
- **TypeScript**: ESLint, Prettier
- **Tests**: Required for new features
- **Documentation**: Update this file for architectural changes

### Pull Request Flow

1. Create feature branch
2. Implement + test locally
3. Run `black . && ruff check . && pytest`
4. Submit PR with clear description
5. CI must pass

---

## 📚 References

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [pgvector](https://github.com/pgvector/pgvector)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [RFC 7807 - Problem Details](https://datatracker.ietf.org/doc/html/rfc7807)

### Design Decisions

| Decision                    | Rationale                                           |
|-----------------------------|-----------------------------------------------------|
| FastAPI over Flask/Django   | Modern, async, auto-generated OpenAPI docs          |
| Next.js App Router          | Latest patterns, React Server Components            |
| pgvector over Pinecone      | Self-hosted, lower latency, cost-effective for MVP  |
| Custom orchestrator         | Flexibility, no LangChain overhead, clearer control |
| Docker Compose              | Simple local dev, easy CI/CD, reproducible          |

---

## 📞 Support

- **Issues**: GitHub Issues
- **Docs**: This file + README.md
- **Code**: Inline comments + docstrings

---

**Built with ❤️ by humans, enhanced by AI agents.**
