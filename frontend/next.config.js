/** @type {import('next').NextConfig} */
const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://doublen-production.up.railway.app'
const apiUrl = /^https?:\/\//.test(rawApiUrl) ? rawApiUrl : `https://${rawApiUrl}`
const normalizedApiUrl = apiUrl.replace(/\/+$/, '')

const nextConfig = {
  output: 'standalone',
  images: { unoptimized: true },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${normalizedApiUrl}/api/:path*`,
      },
    ]
  },
}
module.exports = nextConfig
