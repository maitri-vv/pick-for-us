const basePath = process.env.GITHUB_PAGES === '1' ? '/pick-for-us' : '';

const nextConfig = {
  output: 'export' as const,
  trailingSlash: true,
  images: {unoptimized: true},
  basePath,
  assetPrefix: basePath || undefined,
  env: {NEXT_PUBLIC_BASE_PATH: basePath},
};

export default nextConfig;
