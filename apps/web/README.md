# Decision Calm Web

Next.js 14 frontend for Decision Calm Engine.

## 🚀 Quick Start

### Development

```bash
# Install dependencies
npm install

# Set environment
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Run dev server
npm run dev
```

Open http://localhost:3000

### Docker

```bash
cd ../../  # Go to repo root
docker compose --profile dev up web
```

## 📁 Structure

```
src/
├── app/              # Next.js App Router pages
│   ├── page.tsx      # Landing page with 3-question form
│   ├── session/[id]/ # Decision brief detail page
│   └── history/      # Session history list
├── components/       # React components
│   ├── DecisionForm.tsx
│   ├── DecisionBrief.tsx
│   └── HistoryList.tsx
├── lib/              # Utilities
│   ├── api.ts        # API client
│   ├── types.ts      # TypeScript types
│   └── utils.ts      # Helper functions
└── styles/           # Global CSS with Tailwind
```

## 🧪 Testing

### E2E Tests (Playwright)

```bash
# Install Playwright browsers
npx playwright install

# Run tests
npm run test:e2e

# Run tests in UI mode
npx playwright test --ui
```

### Type Checking

```bash
npm run type-check
```

## 🎨 Styling

- **Framework**: Tailwind CSS
- **Design System**:
  - Colors: `calm-*` palette (blues)
  - Components: Utility classes + custom components in `globals.css`
  - Animations: Fade-in, slide-up

### Key Components

- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary buttons
- `.input-field` - Form inputs
- `.card` - Content cards
- `.badge` - Status badges

## 🔧 Configuration

### Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (required)

### Build

```bash
# Production build
npm run build

# Start production server
npm start
```

## 📊 API Integration

API client in `src/lib/api.ts`:

```typescript
import { apiClient } from '@/lib/api';

// Create session
const session = await apiClient.createDecisionSession({
  context: "...",
  options: "...",
  stress_level: 7,
});

// Get session
const session = await apiClient.getDecisionSession(sessionId);

// List sessions
const sessions = await apiClient.listDecisionSessions();
```

## 🎯 User Flow

1. **Landing** (`/`)
   - Hero with value proposition
   - 3-question form
   - Submit to create session

2. **Decision Brief** (`/session/[id]`)
   - Original context
   - Calm step suggestion
   - Decision options with consequences
   - Control question
   - Next check-in suggestion

3. **History** (`/history`)
   - List of past sessions
   - Quick preview of each
   - Click to view full brief

## 🛡️ Safety Features

- Clear disclaimers on every page
- Crisis hotline numbers in footer
- Non-judgmental language
- User autonomy emphasized

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Touch-friendly UI elements

## 🔍 Code Quality

```bash
# Lint
npm run lint

# Format
npm run format

# Check formatting
npm run format:check
```

## 🤝 Contributing

1. Follow existing component patterns
2. Use TypeScript strictly
3. Test with Playwright for new flows
4. Maintain accessibility (ARIA labels, semantic HTML)

## 📝 Development Notes

- Next.js 14 App Router
- Server Components by default
- Client Components marked with `'use client'`
- Type-safe API calls
- Error boundaries for graceful failures
