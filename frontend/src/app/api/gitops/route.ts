// In: frontend/src/app/api/gitops/route.ts
// This route handler acts as a proxy to the real FastAPI backend.

import { NextRequest, NextResponse } from 'next/server';
import { getApiUrl } from '../../../lib/api-config';

/**
 * Handles POST requests to /api/gitops
 * Forwards the request to the FastAPI backend to get a Git command.
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const apiUrl = getApiUrl('/gitops');
    
    const apiResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!apiResponse.ok) {
      const errorText = await apiResponse.text();
      return new NextResponse(errorText, { status: apiResponse.status });
    }

    const data = await apiResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in proxying to /gitops:', error);
    if (error instanceof Error) {
        return new NextResponse(error.message, { status: 500 });
    }
    return new NextResponse('An unknown error occurred', { status: 500 });
  }
} 