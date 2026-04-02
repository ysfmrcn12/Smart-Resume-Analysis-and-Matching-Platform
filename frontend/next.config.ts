import type { NextConfig } from "next";

const nextConfig = {
  reactCompiler: true,
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
