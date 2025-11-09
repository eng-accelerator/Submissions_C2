# React + Vite Frontend Setup

## Quick Start

### Prerequisites
- Node.js 18+ and npm/yarn/pnpm
- Backend API running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

4. **Open in browser:**
   The app will open at `http://localhost:5173`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

## Features

- ✅ **Accessible UI** - WCAG AA compliant
- ✅ **Real-time Progress** - Streaming updates from backend
- ✅ **Responsive Design** - Works on mobile and desktop
- ✅ **TypeScript** - Type-safe React components
- ✅ **Modern Stack** - React 18 + Vite 5

## Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── ResearchForm.tsx      # Query input form
│   │   ├── ResearchResults.tsx   # Results display
│   │   └── LoadingProgress.tsx   # Progress indicator
│   ├── App.tsx                    # Main app component
│   ├── main.tsx                   # Entry point
│   ├── App.css                    # App styles
│   ├── index.css                  # Global styles
│   └── accessibility.css         # WCAG compliance styles
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Accessibility Features

- **Keyboard Navigation** - Full keyboard support
- **Screen Reader Support** - ARIA labels and roles
- **Focus Management** - Visible focus indicators
- **Color Contrast** - WCAG AA compliant colors
- **Touch Targets** - Minimum 44x44px for mobile
- **Reduced Motion** - Respects user preferences
- **High Contrast** - Supports high contrast mode

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

- `POST /api/research` - Standard research endpoint
- `POST /api/research-stream` - Streaming endpoint with progress
- `GET /api/health` - Health check
- `GET /api/demo-queries` - Pre-configured demo queries

## Development

### Hot Module Replacement
Vite provides instant HMR - changes reflect immediately in the browser.

### TypeScript
All components are written in TypeScript for type safety.

### Linting
```bash
npm run lint
```

## Troubleshooting

**Port already in use?**
- Change port in `vite.config.ts`:
  ```typescript
  server: {
    port: 3000  // Change to available port
  }
  ```

**CORS errors?**
- Ensure backend CORS is configured for `http://localhost:5173`
- Check backend is running on port 8000

**Module not found?**
- Delete `node_modules` and reinstall:
  ```bash
  rm -rf node_modules
  npm install
  ```

---

**For backend setup, see the main README.md**

