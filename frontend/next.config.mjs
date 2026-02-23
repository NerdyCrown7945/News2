const isPages = process.env.GITHUB_ACTIONS === 'true';

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: { unoptimized: true },
  basePath: isPages ? '/ai-scitech-news-digest' : '',
};

export default nextConfig;
