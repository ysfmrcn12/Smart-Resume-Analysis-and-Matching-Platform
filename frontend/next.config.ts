import type { NextConfig } from "next";
import path from 'path';

const nextConfig = {
  reactCompiler: true,
  allowedDevOrigins: ['172.16.1.121'],
  // Hide the floating Next.js development indicators and logo
  devIndicators: false,
  // Allow HMR and dev server access from your local network IP
  turbopack: {
    // We set the root to the directory where next.config.ts is located (__dirname)
    root: path.join(__dirname),
  },
  async rewrites() {
    // Proxy frontend `/api/*` calls to the Flask backend.
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:5000/api/:path*",
      },
    ];
  },
};

// Keep typing strict without relying on custom/unrecognized properties.
// eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
const typedConfig = nextConfig satisfies NextConfig;

export default typedConfig;
