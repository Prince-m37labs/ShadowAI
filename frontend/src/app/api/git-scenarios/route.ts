// In: frontend/src/app/api/git-scenarios/route.ts
// This route handler acts as a proxy to the real FastAPI backend.

import { NextRequest, NextResponse } from 'next/server';
import { getApiUrl } from '../../../lib/api-config';

// Get the real backend URL from a server-side environment variable
// This is not exposed to the public.
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Handles GET requests to /api/git-scenarios
 * Fetches the available Git scenarios from the FastAPI backend.
 */
export async function GET(req: NextRequest) {
  try {
    const apiUrl = getApiUrl('/git-scenarios');
    
    const apiResponse = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!apiResponse.ok) {
      const errorText = await apiResponse.text();
      return new NextResponse(errorText, { status: apiResponse.status });
    }

    const data = await apiResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in proxying to /git-scenarios:', error);
    if (error instanceof Error) {
        return new NextResponse(error.message, { status: 500 });
    }
    return new NextResponse('An unknown error occurred', { status: 500 });
  }
} 