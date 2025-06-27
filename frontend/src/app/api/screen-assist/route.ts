import { NextRequest, NextResponse } from 'next/server';
import { getApiUrl } from '../../../lib/api-config';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const apiUrl = getApiUrl('/screen-assist');
    
    const apiResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!apiResponse.ok) {
      const errorText = await apiResponse.text();
      return NextResponse.json({ error: errorText }, { status: apiResponse.status });
    }

    const data = await apiResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in proxying to /screen-assist:', error);
    if (error instanceof Error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
    return NextResponse.json({ error: 'An unknown error occurred' }, { status: 500 });
  }
} 