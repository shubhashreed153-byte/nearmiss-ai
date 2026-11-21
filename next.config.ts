import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/nearmiss-ai",
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
};

export default nextConfig;