# Next.js Frontend and Flask Backend Setup Guide

## Overview

ResumeRocket now uses a modern architecture with two main components:

1. **Flask Backend**: Provides API endpoints, handles data processing, and manages business logic
2. **Next.js Frontend**: Delivers a responsive user interface with modern React components

This document explains how to work with this architecture, including development workflows and key concepts.

## Project Structure

The project is organized with a clear separation between frontend and backend:

```
ResumeRocket/
├── backend/               # Flask backend API
│   ├── routes/            # API route definitions
│   ├── services/          # Business logic services
│   ├── app.py             # Flask application
│   └── models.py          # SQLAlchemy database models
├── frontend/              # Next.js frontend application
│   ├── public/            # Static assets
│   └── src/
│       ├── app/           # Next.js App Router pages
│       ├── components/    # React components
│       ├── hooks/         # Custom React hooks
│       └── lib/           # Utility functions and API clients
├── dev.py                 # Development script to run both together
└── docs/                  # Documentation
```

## Development Setup

You can develop the frontend and backend independently or run them together.

### Prerequisites

- Python 3.11+ with virtual environment
- Node.js 18+ and npm
- UV package management tool

### Option 1: Running Both Together (Recommended for New Developers)

We provide a development script that starts both the frontend and backend:

```bash
# Activate your virtual environment
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate     # On Windows

# Start both servers with the dev script
uv run python dev.py
```

This will:
- Start the Flask backend on port 8080
- Start the Next.js frontend on port 3000
- Configure them to communicate properly

### Option 2: Running Separately (Advanced)

For more control, you can run each component independently:

#### Backend (Flask):

```bash
# Activate your virtual environment
source .venv/bin/activate

# Install dependencies if needed
uv sync

# Run the Flask application
uv run flask --app backend.app run --port 8080
```

#### Frontend (Next.js):

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies if needed
npm install

# Start the development server
npm run dev
```

The Next.js app will be available at http://localhost:3000, configured to send API requests to the backend at http://localhost:8080.

## Key Concepts

### Next.js App Router

Next.js uses a file-based routing system. The directory structure in `frontend/src/app` defines the routes:

- `app/(public)/page.tsx` → Homepage at "/"
- `app/(auth)/dashboard/page.tsx` → Dashboard at "/dashboard"
- `app/(auth-pages)/login/page.tsx` → Login page at "/login"

The parentheses in the directory names create "route groups" that help organize routes without affecting the URL path.

### Route Groups

The application has three main route groups:

1. `(public)`: Marketing pages and public content
2. `(auth)`: Authenticated pages requiring login
3. `(auth-pages)`: Authentication-related pages (login, register, etc.)

### Client vs. Server Components

Next.js uses a mix of server and client components:

- **Server Components**: Default in Next.js 13+, render on server for better performance
- **Client Components**: Start with `"use client"` directive, can use hooks and interactivity

```tsx
"use client"

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  )
}
```

### API Communication

The frontend communicates with the backend through API calls:

1. **API Services**: Found in `frontend/src/lib/api-services.ts`, manage all API calls
2. **Environment Variables**: `NEXT_PUBLIC_API_URL` controls the API endpoint
3. **Next.js API Routes**: Proxy requests to avoid CORS issues in development

### Authentication Flow

User authentication flows through:

1. **Auth Context**: Provides authentication state to all components
2. **JWT Tokens**: Stored in cookies and localStorage
3. **Protected Routes**: Redirect unauthenticated users to login

## Common Development Tasks

### Adding a New Page

1. Create a new file at `frontend/src/app/(group)/your-page/page.tsx`
2. Export a React component as the default export
3. The page will be available at `/your-page`

### Adding a New API Endpoint

1. Create a new route handler in `backend/routes/`
2. Register it in the Flask application
3. Add a corresponding API service in `frontend/src/lib/api-services.ts`

### Testing API Endpoints

You can test API endpoints with curl:

```bash
# Test health endpoint
curl http://localhost:8080/api/health

# Test with authentication
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8080/api/protected-endpoint
```

## Troubleshooting

### Port Already in Use

If port 5000 is in use (common on macOS):
- Flask runs on port 8080 by default
- To change ports: Edit the `dev.py` script or specify port in the command

### API Connection Issues

If the frontend can't connect to the API:
- Check that both servers are running
- Verify the `NEXT_PUBLIC_API_URL` environment variable
- Check for CORS configuration issues in the backend

### Hot Reload Not Working

For Flask:
- Make sure debug mode is enabled
- Check for syntax errors that might prevent reloading

For Next.js:
- Next.js should reload automatically when files change
- If not, try restarting the development server

## Advanced Configuration

### Environment Variables

Frontend:
- Create `.env.local` in the frontend directory
- Define variables like `NEXT_PUBLIC_API_URL`

Backend:
- Use `.env` file in the root directory
- Access with `os.environ.get('VARIABLE_NAME')`

### Production Deployment

For a production deployment:
1. Build the Next.js app with `npm run build`
2. Configure the Flask app with proper security settings
3. Use a production-ready WSGI server for Flask (like Gunicorn)
4. Set up proper CORS configuration

## Conclusion

This dual-architecture approach separates concerns and lets each technology shine:
- Flask handles the data processing and business logic
- Next.js delivers a modern and responsive UI

By understanding how these components interact, you can efficiently develop new features and maintain the application.