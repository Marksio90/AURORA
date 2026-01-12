# Spokojne Decyzje 🧘

**Podejmuj spokojniejsze decyzje w 60 sekund.**

Platforma MVP klasy światowej dla wieloagentowego, multimodalnego wsparcia decyzyjnego — zaprojektowana, aby pomóc użytkownikom podejmować spokojniejsze, lepsze decyzje bez odbierania im kontroli.

## 🎯 Czym to jest?

Spokojne Decyzje to **System Wsparcia Decyzji** (nie terapia, nie porada medyczna), który:

- Analizuje kontekst Twojej decyzji wykorzystując **5 wyspecjalizowanych agentów AI**
- Prezentuje **3 możliwe ścieżki** z konsekwencjami i ryzykiem emocjonalnym
- Sugeruje **jedną uspokajającą czynność** dopasowaną do Twojego poziomu stresu
- Proponuje **kiedy wrócić do sprawy** (bez manipulacji, pełna autonomia)
- Pamięta poprzednie decyzje dzięki **pamięci wektorowej** dla spersonalizowanego kontekstu

## 🏗️ Architektura

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind
- **Backend**: FastAPI + Python 3.11 + Pydantic v2
- **Baza danych**: PostgreSQL 16 + pgvector
- **AI**: OpenAI GPT-4o-mini (z function calling i streaming)
- **Orkiestracja**: Niestandardowy system wieloagentowy z 5 wyspecjalizowanymi agentami
- **Infrastruktura**: Docker Compose (gotowe na dev i prod)

### System Wieloagentowy

1. **Agent Przyjmujący**: Normalizuje dane wejściowe użytkownika do ustrukturyzowanego schematu
2. **Agent Kontekstowy**: Zadaje 0-2 pytania wyjaśniające (minimalistycznie, bez spamowania)
3. **Agent Spokoju**: Wykrywa przeciążenie i sugeruje "Kroki Uspokajające"
4. **Agent Opcji i Konsekwencji**: Generuje 2-4 opcje z konsekwencjami
5. **Agent Bezpieczeństwa i Etyki**: Blokuje szkodliwe treści, zapewnia nieautorytarny ton

## 🚀 Szybki Start

### Wymagania

- Docker & Docker Compose
- Klucz API OpenAI

### 1. Klonowanie i Konfiguracja

```bash
git clone <repo-url>
cd AURORA
cp .env.example .env
# Edytuj .env i dodaj swój OPENAI_API_KEY
```

### 2. Uruchomienie Platformy

```bash
# Tryb deweloperski (z hot reload dla API i Web)
docker compose --profile dev up --build

# Tryb produkcyjny (zoptymalizowane buildy)
docker compose --profile prod up --build

# Zatrzymanie wszystkich usług
docker compose --profile dev down
```

**Uwaga dla użytkowników Windows**: Upewnij się, że Docker Desktop jest uruchomiony przed wykonaniem tych komend.

### 3. Dostęp

- **Interfejs Web**: http://localhost:3000
- **Dokumentacja API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Struktura Monorepo

```
AURORA/
├── apps/web/              # Frontend Next.js
├── services/api/          # Backend FastAPI + agenty
├── packages/shared/       # Współdzielone typy TypeScript
├── infra/docker/          # Konfiguracje Docker
└── docs/                  # Dokumentacja architektury
```

## 🧪 Rozwój

### Backend (FastAPI)

```bash
cd services/api

# Instalacja zależności
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Uruchomienie migracji
alembic upgrade head

# Uruchomienie testów
pytest

# Linting i formatowanie
ruff check .
black .
mypy src/
```

### Frontend (Next.js)

```bash
cd apps/web

# Instalacja zależności
npm install

# Uruchomienie serwera deweloperskiego
npm run dev

# Uruchomienie testów
npm run test
npm run test:e2e

# Linting i formatowanie
npm run lint
npm run format
```

## 📊 Endpointy API

### Sesje Decyzyjne

- `POST /v1/decision/sessions` - Utwórz nową sesję decyzyjną
- `GET /v1/decision/sessions/{id}` - Pobierz sesję po ID
- `GET /v1/decision/sessions` - Lista wszystkich sesji (paginowana)

### Zdrowie i Monitoring

- `GET /health` - Sprawdzenie stanu zdrowia
- `GET /health/ready` - Sonda gotowości

## 🧠 Jak to Działa (przepływ 60 sekund)

1. **Użytkownik wprowadza**:
   - Kontekst decyzji (tekst)
   - Dostępne opcje
   - Poziom stresu (1-10)

2. **System orkiestruje 5 agentów**:
   - Przyjmujący → Kontekstowy → Spokoju → Opcji → Bezpieczeństwa

3. **Użytkownik otrzymuje**:
   - **Brief Decyzyjny** (1 ekran):
     - 3 wyraźne ścieżki
     - Konsekwencje dla każdej ścieżki
     - Ryzyka emocjonalne
     - Pytanie kontrolne
   - **Krok Uspokajający**: Jedna mała uspokajająca czynność
   - **Następne Sprawdzenie**: Sugerowany czas powrotu

4. **System pamięta**:
   - Przechowuje sesję w Postgres
   - Osadza kontekst w pgvector
   - Wykorzystuje historię do przyszłej personalizacji

## 🛡️ Bezpieczeństwo i Etyka

- ✅ **Bez diagnozy**: To NIE jest porada medyczna/terapeutyczna
- ✅ **Zastrzeżenia**: Jasne granice pokazane w UI
- ✅ **Bezpieczeństwo treści**: Blokuje samookaleczenie, autorytarne polecenia
- ✅ **Autonomia użytkownika**: System prezentuje opcje, nigdy nie rozkazuje
- ✅ **Transparentność**: Użytkownicy widzą rozumowanie, nie czarne skrzynki

## 🔧 Konfiguracja

Cała konfiguracja przez zmienne środowiskowe (zobacz `.env.example`):

- Dane uwierzytelniające API OpenAI
- Połączenie z bazą danych
- Flagi funkcji (wyszukiwanie wektorowe, obserwowalność)
- Profile Docker (dev, prod)

## 📈 Obserwowalność (Opcjonalnie)

Włącz za pomocą `--profile observability`:

```bash
docker compose --profile observability up
```

Zawiera:
- Strukturalne logowanie JSON
- Metryki (gotowe na Prometheus)
- Śledzenie (gotowe na OpenTelemetry)

## 🧪 Testowanie

### Backend
- Testy jednostkowe: `pytest tests/unit/`
- Testy integracyjne: `pytest tests/integration/`
- Pokrycie: `pytest --cov=src`

### Frontend
- Testy jednostkowe: `npm run test`
- Testy E2E: `npm run test:e2e` (Playwright)

### CI/CD
GitHub Actions uruchamia się przy każdym push:
- Sprawdzenie lintingu i formatowania
- Sprawdzenie typów
- Testy jednostkowe + integracyjne
- Buildy Docker

## 📝 Licencja

Licencja MIT - szczegóły w pliku LICENSE.

## 🤝 Współpraca

To kod MVP. Współpraca mile widziana:
1. Forkuj repozytorium
2. Utwórz branch z funkcją
3. Upewnij się, że testy przechodzą
4. Prześlij PR

## ⚠️ Zastrzeżenie

**Spokojne Decyzje NIE JEST**:
- Poradą medyczną
- Terapią zdrowia psychicznego
- Interwencją kryzysową
- Zamiennikiem profesjonalnej pomocy

**W nagłych przypadkach zdrowia psychicznego skontaktuj się**:
- PL: 116 123 (Telefon Zaufania dla Dorosłych)
- PL: 116 111 (Telefon Zaufania dla Dzieci i Młodzieży)
- Twoje lokalne służby ratunkowe

---

Zbudowane z ❤️ przez ludzi, wzmocnione przez agentów AI.
