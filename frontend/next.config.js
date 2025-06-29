import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Handle API proxying for both local and Replit environments
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    
    return [
      {
        source: '/api/backend/:path*',
        destination: `${backendUrl}/:path*`,
      },
      {
        source: '/screen-assist',
        destination: `${backendUrl}/screen-assist`,
      },
    ];
  },
  
  // Environment variables
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
  },
};

export default nextConfig;
