# syntax=docker/dockerfile:1
# ── Dev stage: Vite dev server (used in docker-compose locally) ──────────────
FROM node:20-alpine AS dev
WORKDIR /app
COPY package*.json ./
RUN npm ci --prefer-offline --no-audit
COPY . .
EXPOSE 5174
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5174"]

# ── Prod stage: Build static assets (used in CI / Vercel deploy) ─────────────
FROM dev AS build-stage
ARG VITE_API_BASE=https://vcareer-ops-production.up.railway.app
ENV VITE_API_BASE=$VITE_API_BASE
RUN npm run build

FROM nginx:alpine AS prod
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
