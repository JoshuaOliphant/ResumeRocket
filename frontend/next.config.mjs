/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8080/api/:path*',
      },
      {
        source: '/auth/:path*',
        destination: 'http://localhost:8080/auth/:path*',
      },
    ];
  },
  // Environment variables available on the client side
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  },
  // Enable React strict mode for better development experience
  reactStrictMode: true,
};

export default nextConfig;
