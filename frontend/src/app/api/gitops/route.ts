// In: frontend/src/app/api/gitops/route.ts
// This route handler acts as a proxy to the real FastAPI backend.

import { NextResponse } from 'next/server';

// Get the real backend URL from a server-side environment variable
// This is not exposed to the public.
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Handles POST requests to /api/gitops
 * Forwards the request to the FastAPI backend to get a Git command.
 */
export async function POST(request: Request) {
  try {
    const requestBody = await request.json();

    const apiResponse = await fetch(`${BACKEND_URL}/gitops`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
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