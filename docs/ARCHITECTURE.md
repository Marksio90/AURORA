# Spokojne Decyzje - Architektura

**Wersja:** 0.1.0 (MVP)
**Ostatnia aktualizacja:** 2024-01-12

## 🎯 Misja

Umożliwienie użytkownikom podejmowania **spokojniejszych, lepszych decyzji** w 60 sekund poprzez wieloagentowy system AI, który:
- Analizuje kontekst decyzji bez uprzedzeń
- Prezentuje opcje z konsekwencjami, nie polecenia
- Sugeruje działania uspokajające na podstawie stanu emocjonalnego
- W pełni szanuje autonomię użytkownika

**To NIE JEST**: Porada medyczna, terapia, interwencja kryzysowa ani diagnoza.

---

## 🏗️ Architektura Systemu

### Ogólny Przegląd

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Przeglądarka│────────▶│   Next.js    │────────▶│   FastAPI   │
│ (Użytkownik) │◀────────│  Frontend    │◀────────│   Backend   │
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

### Stos Technologiczny

| Warstwa        | Technologia                    | Wersja   |
|----------------|--------------------------------|----------|
| Frontend       | Next.js (App Router)           | 14.1     |
| Backend        | FastAPI                        | 0.109+   |
| Baza danych    | PostgreSQL + pgvector          | 16       |
| Dostawca AI    | OpenAI (GPT-4o-mini)           | Najnowsza|
| Orkiestracja   | Niestandardowa (inspirowana LangGraph) | -  |
| Infrastruktura | Docker Compose                 | 3.9      |
| Język          | TypeScript (FE), Python (BE)   | TS5, Py3.11 |

---

## 📊 System Wieloagentowy

### Graf Agentów

```
Dane Wejściowe Użytkownika (3 Pytania)
        ↓
┌───────────────────────┐
│ Agent Przyjmujący     │ → Normalizacja i strukturyzacja danych wejściowych
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Agent Kontekstowy     │ → Sprawdzenie czy potrzebne wyjaśnienie (0-2 pytania)
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Agent Spokoju         │ → Generowanie "Kroku Uspokajającego" na podstawie stresu (1-10)
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Agent Opcji           │ → Generowanie 2-4 opcji + konsekwencje + ryzyka
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Agent Bezpieczeństwa  │ → Walidacja treści, blokowanie szkodliwych wzorców
└───────────┬───────────┘
            ↓
    Brief Decyzyjny
```

### Odpowiedzialności Agentów

| Agent              | Wejście                        | Wyjście                               | Temperature |
|--------------------|--------------------------------|---------------------------------------|-------------|
| **Przyjmujący**    | Surowy tekst użytkownika       | Strukturalny JSON (decyzja, opcje)    | 0.3         |
| **Kontekstowy**    | Strukturalne dane wejściowe    | 0-2 pytania wyjaśniające (jeśli potrzeba) | 0.3     |
| **Spokoju**        | Kontekst + poziom stresu       | Krok uspokajający (oddychanie, przerwa, etc.) | 0.7 |
| **Opcji**          | Kontekst + ograniczenia        | 2-4 opcje + konsekwencje + ryzyka     | 0.7         |
| **Bezpieczeństwa** | Cała treść                     | Walidacja bezpieczeństwa + sprawdzenie tonu | 0.2   |

### Zasady Bezpieczeństwa

1. **Blokowanie Treści**:
   - Słowa kluczowe samookaleczenia → Blokada + przekierowanie do zasobów kryzysowych
   - Diagnozy medyczne → Blokada z zastrzeżeniem
   - Autorytarne polecenia → Usunięcie/przepisanie

2. **Walidacja Tonu**:
   - Odrzucaj: "musisz", "powinieneś", "zrób to teraz"
   - Akceptuj: "możesz rozważyć", "jedną opcją jest", "mógłbyś"

3. **Zastrzeżenia**:
   - Zawsze obecne w każdym Briefie Decyzyjnym
   - Numery infolinii kryzysowych w stopce

---

## 🗄️ Schemat Bazy Danych

### Tabela `decision_sessions`

```sql
CREATE TABLE decision_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Użytkownik (anonimowe śledzenie)
    user_id VARCHAR(255),

    -- Dane wejściowe
    context TEXT NOT NULL,
    options TEXT NOT NULL,
    stress_level INTEGER NOT NULL CHECK (stress_level BETWEEN 1 AND 10),

    -- Wyjście
    decision_brief JSONB,

    -- Metadane
    processing_time_seconds FLOAT,
    tags JSONB DEFAULT '[]',

    -- Wyszukiwanie wektorowe (1536 wymiarów = text-embedding-3-small)
    embedding vector(1536),

    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Indeks podobieństwa wektorowego (IVFFlat dla szybkości)
CREATE INDEX idx_embedding ON decision_sessions
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Wyszukiwanie Wektorowe

**Cel**: Znajdowanie podobnych poprzednich decyzji dla personalizacji.

**Przepływ**:
1. Osadzenie kontekstu + opcji użytkownika → wektor 1536-wymiarowy
2. Przechowanie w kolumnie `embedding`
3. W przyszłych sesjach, pobranie top-3 podobnych poprzednich decyzji
4. Użycie jako kontekst dla agentów (opcjonalne ulepszenie)

**Metryka Odległości**: Podobieństwo kosinusowe (przez pgvector)

---

## 🔄 Przepływ Danych

### 1. Tworzenie Sesji Decyzyjnej

```
POST /v1/decision/sessions
{
  "context": "Czy powinienem zmienić pracę?",
  "options": "Zostać, Odejść, Negocjować",
  "stress_level": 7
}
```

**Przepływ Backendu**:
1. Walidacja danych wejściowych (Pydantic)
2. Przekazanie do `DecisionOrchestrator`
3. Orkiestrator uruchamia 5 agentów sekwencyjnie
4. Składanie `DecisionBrief`
5. Przechowanie w Postgres
6. Generowanie osadzenia (async)
7. Zwrócenie Briefu Decyzyjnego

**Odpowiedź**:
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

### 2. Pobieranie Sesji

```
GET /v1/decision/sessions/{id}
```

Pobranie z Postgres, zwrócenie pełnej sesji + Briefu Decyzyjnego.

### 3. Lista Sesji

```
GET /v1/decision/sessions?user_id=abc&page=1&page_size=20
```

Paginowana lista poprzednich sesji użytkownika.

---

## 🌐 Architektura Frontendu

### Strony (Next.js App Router)

| Trasa              | Komponent         | Cel                              |
|--------------------|-------------------|----------------------------------|
| `/`                | `page.tsx`        | Strona główna + formularz 3 pytań|
| `/session/[id]`    | `page.tsx`        | Widok szczegółów Briefu Decyzyjnego |
| `/history`         | `page.tsx`        | Lista poprzednich sesji          |

### Komponenty

- **DecisionForm**: Formularz 3 pytań z walidacją
- **DecisionBrief**: Wyświetlanie opcji, kroku uspokajającego, pytania kontrolnego
- **HistoryList**: Lista poprzednich sesji z podglądami

### Zarządzanie Stanem

- **Stan Lokalny**: React `useState` dla formularzy
- **Klient API**: Scentralizowany w `lib/api.ts`
- **Brak potrzeby biblioteki stanu globalnego dla MVP**

---

## 🚀 Wdrożenie

### Docker Compose (Rozwój Lokalny)

```bash
docker compose --profile dev up --build
```

**Usługi**:
- `postgres`: PostgreSQL 16 + pgvector
- `api`: Backend FastAPI
- `web`: Frontend Next.js

**Profile**:
- `dev`: Tryb deweloperski (hot reload)
- `prod`: Tryb produkcyjny (zoptymalizowane buildy)
- `observability`: Dodaje metryki/śledzenie (opcjonalnie)

### Zmienne Środowiskowe

Zobacz `.env.example` dla pełnej listy. **Wymagane**:
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `NEXT_PUBLIC_API_URL`

### Migracje

```bash
# Zastosowanie migracji
alembic upgrade head

# Utworzenie nowej migracji
alembic revision --autogenerate -m "opis"
```

---

## 🧪 Strategia Testowania

### Backend

| Typ           | Narzędzie | Pokrycie      |
|---------------|-----------|---------------|
| Jednostkowe   | pytest    | Agenty, utils |
| Integracyjne  | pytest    | Endpointy API |
| Kontraktowe   | OpenAPI   | Testy schematu|

**Uruchomienie Testów**:
```bash
cd services/api
pytest --cov=src
```

### Frontend

| Typ           | Narzędzie  | Pokrycie              |
|---------------|------------|-----------------------|
| E2E           | Playwright | Pełne przepływy użytkownika |
| Jednostkowe   | Vitest     | Komponenty (przyszłość) |

**Uruchomienie E2E**:
```bash
cd apps/web
npm run test:e2e
```

### CI/CD

GitHub Actions uruchamia się przy każdym push:
1. Linting (ruff, eslint)
2. Sprawdzanie typów (mypy, tsc)
3. Testy jednostkowe
4. Buildy Docker

---

## 🔐 Bezpieczeństwo i Prywatność

### Ochrona Danych

- **Brak wymaganego PII**: Anonimowe śledzenie użytkownika (opcjonalny `user_id`)
- **Brak cookies sesji**: Bezstanowe API
- **Tylko HTTPS w produkcji**

### Bezpieczeństwo API

- **Walidacja danych wejściowych**: Schematy Pydantic
- **Ograniczenie szybkości**: Opcjonalne (przez Redis)
- **CORS**: Tylko skonfigurowane originy
- **Ochrona przed SQL injection**: ORM SQLAlchemy

### Bezpieczeństwo Treści

- **Blokowanie słów kluczowych**: Filtrowanie niebezpiecznej treści
- **Moderacja OpenAI**: Można dodać API moderacji (przyszłość)
- **Zastrzeżenia**: Zawsze widoczne

---

## 📈 Obserwowalność (Opcjonalnie)

### Logowanie

**Format**: Strukturalny JSON (przez `structlog`)

**Pola**:
- `timestamp`, `level`, `message`
- `agent_name`, `session_id`, `duration_ms`
- `error`, `stack_trace` (przy błędach)

**Wyjście**: stdout (przechwytywane przez logi Docker)

### Metryki (Przyszłość)

- Opóźnienie żądań (p50, p95, p99)
- Czas przetwarzania agentów
- Wskaźniki błędów
- Użycie tokenów OpenAI

**Narzędzia**: Prometheus + Grafana

---

## 🛣️ Mapa Drogowa (Post-MVP)

### Faza 2: Ulepszona Personalizacja
- Użycie wyszukiwania wektorowego dla kontekstowych rekomendacji
- Wykrywanie wzorców w historii użytkownika
- Wglądy "Już miałeś podobne decyzje wcześniej"

### Faza 3: Dane Wejściowe Multimodalne
- Wejście głosowe → transkrypcja → przetwarzanie
- Przesyłanie obrazów → OCR → ekstrakcja kontekstu
- Wsparcie dla nietekstowych artefaktów decyzyjnych

### Faza 4: Współpraca
- Udostępnianie Briefów Decyzyjnych zaufanym doradcom
- Anonimowy feedback rówieśników (opcjonalnie)
- Eksport decyzji do PDF/markdown

### Faza 5: Zaawansowane Bezpieczeństwo
- Integracja API Moderacji OpenAI
- Niestandardowy dostrojony klasyfikator bezpieczeństwa
- Wykrywanie kryzysu w czasie rzeczywistym z eskalacją

---

## 🤝 Współpraca

### Standardy Kodu

- **Python**: Black, Ruff, MyPy
- **TypeScript**: ESLint, Prettier
- **Testy**: Wymagane dla nowych funkcji
- **Dokumentacja**: Aktualizuj ten plik dla zmian architektonicznych

### Przepływ Pull Request

1. Utwórz branch z funkcją
2. Implementuj + testuj lokalnie
3. Uruchom `black . && ruff check . && pytest`
4. Prześlij PR z jasnym opisem
5. CI musi przejść

---

## 📚 Referencje

### Zasoby Zewnętrzne

- [Dokumentacja FastAPI](https://fastapi.tiangolo.com/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [pgvector](https://github.com/pgvector/pgvector)
- [Referencja API OpenAI](https://platform.openai.com/docs/api-reference)
- [RFC 7807 - Problem Details](https://datatracker.ietf.org/doc/html/rfc7807)

### Decyzje Projektowe

| Decyzja                     | Uzasadnienie                                        |
|-----------------------------|-----------------------------------------------------|
| FastAPI zamiast Flask/Django| Nowoczesne, async, automatycznie generowane dokumenty OpenAPI |
| Next.js App Router          | Najnowsze wzorce, React Server Components           |
| pgvector zamiast Pinecone   | Self-hosted, niższe opóźnienie, opłacalne dla MVP   |
| Niestandardowy orkiestrator | Elastyczność, brak narzutu LangChain, jaśniejsza kontrola |
| Docker Compose              | Prosty rozwój lokalny, łatwe CI/CD, reprodukowalne |

---

## 📞 Wsparcie

- **Problemy**: GitHub Issues
- **Dokumentacja**: Ten plik + README.md
- **Kod**: Komentarze inline + docstringi

---

**Zbudowane z ❤️ przez ludzi, wzmocnione przez agentów AI.**
