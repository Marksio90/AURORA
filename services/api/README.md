# Decision Calm API

FastAPI backend for Decision Calm Engine - Multi-agent decision support system.

## 🏗️ Architecture

```
src/
├── agents/           # 5 specialized agents (Intake, Context, Calmness, Options, Safety)
├── orchestrator/     # Multi-agent orchestration with state management
├── api/              # FastAPI routes and middleware
├── db/               # SQLAlchemy models, pgvector integration
├── core/             # Config, logging, error handling
├── schemas/          # Pydantic v2 schemas
└── services/         # OpenAI client, business logic
```

## 🚀 Quick Start

### Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/decisioncalm"
export OPENAI_API_KEY="sk-..."

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload
```

### Docker Development

```bash
cd ../../  # Go to repo root
docker compose --profile dev up --build
```

API available at: http://localhost:8000

## 📊 API Endpoints

### Health

- `GET /v1/health` - Health check
- `GET /v1/health/ready` - Readiness probe

### Decisions

- `POST /v1/decision/sessions` - Create decision session
- `GET /v1/decision/sessions/{id}` - Get session by ID
- `GET /v1/decision/sessions` - List sessions (paginated)

Full API docs: http://localhost:8000/docs

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py

# Run integration tests only
pytest tests/integration/
```

## 🔧 Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy src/

# Run all checks
black . && ruff check . && mypy src/ && pytest
```

## 🔄 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🧠 Multi-Agent System

### Agent Flow

```
User Input
    ↓
[Intake Agent] → Normalize & structure input
    ↓
[Context Agent] → Check if clarification needed (0-2 questions)
    ↓
[Calmness Agent] → Generate calm step based on stress level
    ↓
[Options Agent] → Generate 2-4 decision options + consequences
    ↓
[Safety Agent] → Validate content safety & tone
    ↓
Decision Brief (returned to user)
```

### Agent Responsibilities

- **Intake**: Parses user input into structured format
- **Context**: Asks minimal clarifying questions (MVP: skips in most cases)
- **Calmness**: Suggests calming actions based on stress (1-10 scale)
- **Options**: Generates 2-4 options with consequences and emotional risk
- **Safety**: Blocks harmful content, ensures non-authoritarian tone

## 🛡️ Safety Features

- **Content Safety**: Blocks self-harm, violence, medical diagnoses
- **Tone Validation**: Removes authoritarian language ("you must", "you should")
- **Disclaimers**: Always includes safety disclaimers
- **Crisis Detection**: Redirects to crisis resources when needed

## 📈 Observability

Structured JSON logging with:
- Request/response timing
- Agent execution traces
- Error tracking
- Performance metrics

Log level controlled via `LOG_LEVEL` env var.

## 🔐 Security

- Pydantic validation on all inputs
- SQL injection protection (SQLAlchemy)
- CORS configuration
- Rate limiting (optional, via Redis)
- Problem+JSON error responses (RFC 7807)

## 🌐 Environment Variables

See `.env.example` at repo root for all configuration options.

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key

Optional:
- `REDIS_ENABLED` - Enable Redis for caching
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENABLE_VECTOR_SEARCH` - Enable pgvector similarity search

## 📝 Development Notes

- Python 3.11+
- FastAPI 0.109+
- Pydantic v2
- SQLAlchemy 2.0 (async)
- PostgreSQL 16 + pgvector
- OpenAI API (gpt-4o-mini)

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests and linting
4. Submit PR

All PRs must:
- Pass CI (lint + tests)
- Maintain >80% code coverage
- Follow existing code style
