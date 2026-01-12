# Spokojne Decyzje Web

Frontend Next.js 14 dla Spokojnych Decyzji.

## 🚀 Szybki Start

### Rozwój

```bash
# Instalacja zależności
npm install

# Ustawienie środowiska
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Uruchomienie serwera deweloperskiego
npm run dev
```

Otwórz http://localhost:3000

### Docker

```bash
cd ../../  # Przejdź do katalogu głównego repozytorium
docker compose --profile dev up web
```

## 📁 Struktura

```
src/
├── app/              # Strony Next.js App Router
│   ├── page.tsx      # Strona główna z formularzem 3 pytań
│   ├── session/[id]/ # Strona szczegółów briefu decyzyjnego
│   └── history/      # Lista historii sesji
├── components/       # Komponenty React
│   ├── DecisionForm.tsx
│   ├── DecisionBrief.tsx
│   └── HistoryList.tsx
├── lib/              # Narzędzia
│   ├── api.ts        # Klient API
│   ├── types.ts      # Typy TypeScript
│   └── utils.ts      # Funkcje pomocnicze
└── styles/           # Globalny CSS z Tailwind
```

## 🧪 Testowanie

### Testy E2E (Playwright)

```bash
# Instalacja przeglądarek Playwright
npx playwright install

# Uruchomienie testów
npm run test:e2e

# Uruchomienie testów w trybie UI
npx playwright test --ui
```

### Sprawdzanie Typów

```bash
npm run type-check
```

## 🎨 Stylizacja

- **Framework**: Tailwind CSS
- **System Projektowy**:
  - Kolory: paleta `calm-*` (niebieskie)
  - Komponenty: Klasy użytkowe + niestandardowe komponenty w `globals.css`
  - Animacje: Fade-in, slide-up

### Kluczowe Komponenty

- `.btn-primary` - Główne przyciski akcji
- `.btn-secondary` - Przyciski drugorzędne
- `.input-field` - Pola formularza
- `.card` - Karty treści
- `.badge` - Znaczniki statusu

## 🔧 Konfiguracja

### Zmienne Środowiskowe

- `NEXT_PUBLIC_API_URL` - URL API backendu (wymagane)

### Build

```bash
# Build produkcyjny
npm run build

# Uruchomienie serwera produkcyjnego
npm start
```

## 📊 Integracja API

Klient API w `src/lib/api.ts`:

```typescript
import { apiClient } from '@/lib/api';

// Tworzenie sesji
const session = await apiClient.createDecisionSession({
  context: "...",
  options: "...",
  stress_level: 7,
});

// Pobieranie sesji
const session = await apiClient.getDecisionSession(sessionId);

// Lista sesji
const sessions = await apiClient.listDecisionSessions();
```

## 🎯 Przepływ Użytkownika

1. **Strona Główna** (`/`)
   - Hero z propozycją wartości
   - Formularz 3 pytań
   - Przesłanie do utworzenia sesji

2. **Brief Decyzyjny** (`/session/[id]`)
   - Oryginalny kontekst
   - Sugestia kroku uspokajającego
   - Opcje decyzji z konsekwencjami
   - Pytanie kontrolne
   - Sugestia następnego sprawdzenia

3. **Historia** (`/history`)
   - Lista poprzednich sesji
   - Szybki podgląd każdej
   - Kliknięcie, aby zobaczyć pełny brief

## 🛡️ Funkcje Bezpieczeństwa

- Wyraźne zastrzeżenia na każdej stronie
- Numery infolinii kryzysowych w stopce
- Język bez osądzania
- Podkreślona autonomia użytkownika

## 📱 Design Responsywny

- Podejście mobile-first
- Breakpointy: sm (640px), md (768px), lg (1024px)
- Elementy UI przyjazne dla dotyku

## 🔍 Jakość Kodu

```bash
# Linting
npm run lint

# Formatowanie
npm run format

# Sprawdzenie formatowania
npm run format:check
```

## 🤝 Współpraca

1. Postępuj zgodnie z istniejącymi wzorcami komponentów
2. Używaj TypeScript ściśle
3. Testuj z Playwright dla nowych przepływów
4. Utrzymuj dostępność (etykiety ARIA, semantyczny HTML)

## 📝 Notatki Deweloperskie

- Next.js 14 App Router
- Server Components domyślnie
- Client Components oznaczone przez `'use client'`
- Bezpieczne typowo wywołania API
- Error boundaries dla łagodnych błędów
