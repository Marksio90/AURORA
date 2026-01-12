# Decision Calm Engine 🧘

**Podejmuj spokojniejsze decyzje w 60 sekund.**

World-class MVP platform for multiagent, multimodal decision support — designed to help users make calmer, better decisions without taking control away from humans.

## 🎯 What is this?

Decision Calm Engine is a **Decision Support System** (not therapy, not medical advice) that:

- Analyzes your decision context using **5 specialized AI agents**
- Presents **3 possible paths** with consequences and emotional risks
- Suggests **one calming action** tailored to your stress level
- Proposes **when to check back** (no manipulation, full autonomy)
- Remembers past decisions via **vector memory** for personalized context

## 🏗️ Architecture

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind
- **Backend**: FastAPI + Python 3.11 + Pydantic v2
- **Database**: PostgreSQL 16 + pgvector
- **AI**: OpenAI GPT-4o-mini (with function calling & streaming)
- **Orchestration**: Custom multi-agent system with 5 specialized agents
- **Infrastructure**: Docker Compose (local dev & prod ready)

### Multi-Agent System

1. **Intake Agent**: Normalizes user input into structured schema
2. **Context Agent**: Asks 0-2 clarifying questions (minimal, non-spammy)
3. **Calmness Agent**: Detects overload and suggests "Calm Steps"
4. **Options & Consequences Agent**: Generates 2-4 options with consequences
5. **Safety & Ethics Agent**: Blocks harmful content, ensures non-authoritarian tone

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key

### 1. Clone & Configure

```bash
git clone <repo-url>
cd AURORA
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Start the Platform

```bash
# Development mode (with hot reload)
docker compose --profile dev up --build

# Production mode
docker compose --profile prod up --build
```

### 3. Access

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Monorepo Structure

```
AURORA/
├── apps/web/              # Next.js frontend
├── services/api/          # FastAPI backend + agents
├── packages/shared/       # Shared TypeScript types
├── infra/docker/          # Docker configs
└── docs/                  # Architecture docs
```

## 🧪 Development

### Backend (FastAPI)

```bash
cd services/api

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run migrations
alembic upgrade head

# Run tests
pytest

# Lint & format
ruff check .
black .
mypy src/
```

### Frontend (Next.js)

```bash
cd apps/web

# Install dependencies
npm install

# Run dev server
npm run dev

# Run tests
npm run test
npm run test:e2e

# Lint & format
npm run lint
npm run format
```

## 📊 API Endpoints

### Decision Sessions

- `POST /v1/decision/sessions` - Create new decision session
- `GET /v1/decision/sessions/{id}` - Get session by ID
- `GET /v1/decision/sessions` - List all sessions (paginated)

### Health & Monitoring

- `GET /health` - Health check
- `GET /health/ready` - Readiness probe

## 🧠 How It Works (60 seconds flow)

1. **User enters**:
   - Decision context (text)
   - Available options
   - Stress level (1-10)

2. **System orchestrates 5 agents**:
   - Intake → Context → Calmness → Options → Safety

3. **User receives**:
   - **Decision Brief** (1 screen):
     - 3 clear paths
     - Consequences per path
     - Emotional risks
     - Control question
   - **Calm Step**: One small calming action
   - **Next Check-in**: Suggested return time

4. **System remembers**:
   - Stores session in Postgres
   - Embeds context in pgvector
   - Uses history for future personalization

## 🛡️ Safety & Ethics

- ✅ **No diagnosis**: This is NOT medical/therapeutic advice
- ✅ **Disclaimers**: Clear boundaries shown in UI
- ✅ **Content safety**: Blocks self-harm, authoritarian commands
- ✅ **User autonomy**: System presents options, never commands
- ✅ **Transparency**: Users see reasoning, not black boxes

## 🔧 Configuration

All configuration via environment variables (see `.env.example`):

- OpenAI API credentials
- Database connection
- Feature flags (vector search, observability)
- Docker profiles (dev, prod)

## 📈 Observability (Optional)

Enable with `--profile observability`:

```bash
docker compose --profile observability up
```

Includes:
- Structured JSON logging
- Metrics (Prometheus ready)
- Tracing (OpenTelemetry ready)

## 🧪 Testing

### Backend
- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- Coverage: `pytest --cov=src`

### Frontend
- Unit tests: `npm run test`
- E2E tests: `npm run test:e2e` (Playwright)

### CI/CD
GitHub Actions runs on every push:
- Lint & format checks
- Type checking
- Unit + integration tests
- Docker builds

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

This is MVP code. Contributions welcome:
1. Fork repo
2. Create feature branch
3. Ensure tests pass
4. Submit PR

## ⚠️ Disclaimer

**Decision Calm Engine is NOT**:
- Medical advice
- Mental health therapy
- Crisis intervention
- A replacement for professional help

**For mental health emergencies, contact**:
- US: 988 (Suicide & Crisis Lifeline)
- EU: 116 123 (Emotional support)
- Your local emergency services

---

Built with ❤️ by humans, enhanced by AI agents.
