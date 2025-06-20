// In: frontend/src/app/api/git-scenarios/route.ts
// This route handler acts as a proxy to the real FastAPI backend.

import { NextResponse } from 'next/server';

// Get the real backend URL from a server-side environment variable
// This is not exposed to the public.
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Handles GET requests to /api/git-scenarios
 * Fetches the available Git scenarios from the FastAPI backend.
 */
export async function GET() {
  try {
    const apiResponse = await fetch(`${BACKEND_URL}/git-scenarios`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!apiResponse.ok) {
      const errorBody = await apiResponse.json();
      return NextResponse.json({ error: errorBody.detail || 'Backend error' }, { status: apiResponse.status });
    }

    const data = await apiResponse.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('API Route Error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
} 