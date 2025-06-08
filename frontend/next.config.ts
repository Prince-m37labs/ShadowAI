import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/screen-assist',
        destination: 'http://localhost:8000/screen-assist',
      },
    ];
  },
};

export default nextConfig;
