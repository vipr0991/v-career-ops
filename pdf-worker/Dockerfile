# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/playwright:v1.55.0-noble
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY src ./src
USER pwuser
CMD ["node", "src/worker.mjs"]
