// In: frontend/src/app/api/git-scenarios/route.ts
// This route handler acts as a proxy to the real FastAPI backend.

import { NextResponse } from 'next/server';
import { getApiUrl } from '../../../lib/api-config';

/**
 * Handles GET requests to /api/git-scenarios
 * Fetches the available Git scenarios from the FastAPI backend.
 */
export async function GET() {
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