# syntax=docker/dockerfile:1
# Playwright image ships Chromium + all native libs preinstalled.
# Pin the tag to the playwright package version in package.json.
FROM mcr.microsoft.com/playwright:v1.55.0-noble
WORKDIR /app
ENV NODE_ENV=production \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY src ./src
USER pwuser
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s \
  CMD node -e "process.exit(0)"
CMD ["node", "src/worker.mjs"]
