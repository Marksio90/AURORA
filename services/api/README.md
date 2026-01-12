# Spokojne Decyzje API

Backend FastAPI dla Spokojnych Decyzji - System wsparcia decyzji wieloagentowy.

## 🏗️ Architektura

```
src/
├── agents/           # 5 wyspecjalizowanych agentów (Intake, Context, Calmness, Options, Safety)
├── orchestrator/     # Orkiestracja wieloagentowa z zarządzaniem stanem
├── api/              # Trasy FastAPI i middleware
├── db/               # Modele SQLAlchemy, integracja pgvector
├── core/             # Config, logowanie, obsługa błędów
├── schemas/          # Schematy Pydantic v2
└── services/         # Klient OpenAI, logika biznesowa
```

## 🚀 Szybki Start

### Rozwój Lokalny (bez Docker)

```bash
# Instalacja zależności
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Ustawienie zmiennych środowiskowych
export DATABASE_URL="postgresql://user:pass@localhost:5432/decisioncalm"
export OPENAI_API_KEY="sk-..."

# Uruchomienie migracji
alembic upgrade head

# Uruchomienie serwera
uvicorn src.main:app --reload
```

### Rozwój Docker

```bash
cd ../../  # Przejdź do katalogu głównego repozytorium
docker compose --profile dev up --build
```

API dostępne pod: http://localhost:8000

## 📊 Endpointy API

### Zdrowie

- `GET /v1/health` - Sprawdzenie stanu zdrowia
- `GET /v1/health/ready` - Sonda gotowości

### Decyzje

- `POST /v1/decision/sessions` - Utwórz sesję decyzyjną
- `GET /v1/decision/sessions/{id}` - Pobierz sesję po ID
- `GET /v1/decision/sessions` - Lista sesji (paginowana)

Pełna dokumentacja API: http://localhost:8000/docs

## 🧪 Testowanie

```bash
# Uruchomienie wszystkich testów
pytest

# Uruchomienie z pokryciem
pytest --cov=src --cov-report=html

# Uruchomienie konkretnego pliku testów
pytest tests/unit/test_agents.py

# Uruchomienie tylko testów integracyjnych
pytest tests/integration/
```

## 🔧 Jakość Kodu

```bash
# Formatowanie kodu
black .

# Linting
ruff check .

# Sprawdzanie typów
mypy src/

# Uruchomienie wszystkich sprawdzeń
black . && ruff check . && mypy src/ && pytest
```

## 🔄 Migracje Bazy Danych

```bash
# Utworzenie nowej migracji
alembic revision --autogenerate -m "opis"

# Zastosowanie migracji
alembic upgrade head

# Cofnięcie
alembic downgrade -1
```

## 🧠 System Wieloagentowy

### Przepływ Agentów

```
Dane Wejściowe Użytkownika
    ↓
[Agent Przyjmujący] → Normalizacja i strukturyzacja danych wejściowych
    ↓
[Agent Kontekstowy] → Sprawdzenie czy potrzebne wyjaśnienie (0-2 pytania)
    ↓
[Agent Spokoju] → Generowanie kroku uspokajającego na podstawie poziomu stresu
    ↓
[Agent Opcji] → Generowanie 2-4 opcji decyzji + konsekwencje
    ↓
[Agent Bezpieczeństwa] → Walidacja bezpieczeństwa treści i tonu
    ↓
Brief Decyzyjny (zwrócony użytkownikowi)
```

### Odpowiedzialności Agentów

- **Przyjmujący**: Parsuje dane wejściowe użytkownika do ustrukturyzowanego formatu
- **Kontekstowy**: Zadaje minimalne pytania wyjaśniające (MVP: pomija w większości przypadków)
- **Spokoju**: Sugeruje działania uspokajające na podstawie stresu (skala 1-10)
- **Opcji**: Generuje 2-4 opcje z konsekwencjami i ryzykiem emocjonalnym
- **Bezpieczeństwa**: Blokuje szkodliwe treści, zapewnia nieautorytarny ton

## 🛡️ Funkcje Bezpieczeństwa

- **Bezpieczeństwo Treści**: Blokuje samookaleczenie, przemoc, diagnozy medyczne
- **Walidacja Tonu**: Usuwa język autorytarny ("musisz", "powinieneś")
- **Zastrzeżenia**: Zawsze zawiera zastrzeżenia bezpieczeństwa
- **Wykrywanie Kryzysu**: Przekierowuje do zasobów kryzysowych gdy potrzeba

## 📈 Obserwowalność

Strukturalne logowanie JSON z:
- Czasem żądania/odpowiedzi
- Śladami wykonania agentów
- Śledzeniem błędów
- Metrykami wydajności

Poziom logowania kontrolowany przez zmienną środowiskową `LOG_LEVEL`.

## 🔐 Bezpieczeństwo

- Walidacja Pydantic na wszystkich danych wejściowych
- Ochrona przed SQL injection (SQLAlchemy)
- Konfiguracja CORS
- Ograniczenie szybkości (opcjonalne, przez Redis)
- Odpowiedzi błędów Problem+JSON (RFC 7807)

## 🌐 Zmienne Środowiskowe

Zobacz `.env.example` w katalogu głównym repozytorium dla wszystkich opcji konfiguracji.

Wymagane:
- `DATABASE_URL` - String połączenia PostgreSQL
- `OPENAI_API_KEY` - Klucz API OpenAI

Opcjonalne:
- `REDIS_ENABLED` - Włącz Redis dla cache'owania
- `LOG_LEVEL` - Poziom logowania (DEBUG, INFO, WARNING, ERROR)
- `ENABLE_VECTOR_SEARCH` - Włącz wyszukiwanie podobieństwa pgvector

## 📝 Notatki Deweloperskie

- Python 3.11+
- FastAPI 0.109+
- Pydantic v2
- SQLAlchemy 2.0 (async)
- PostgreSQL 16 + pgvector
- OpenAI API (gpt-4o-mini)

## 🤝 Współpraca

1. Utwórz branch z funkcją
2. Wprowadź zmiany
3. Uruchom testy i linting
4. Prześlij PR

Wszystkie PR muszą:
- Przejść CI (lint + testy)
- Utrzymać >80% pokrycia kodu
- Postępować zgodnie z istniejącym stylem kodu
