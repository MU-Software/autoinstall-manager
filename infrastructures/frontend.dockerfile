# Frontend Builder
FROM node:22-alpine AS frontend-builder
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

COPY ../frontend /app
RUN rm -rf /app/node_modules
WORKDIR /app
RUN pnpm fetch
RUN pnpm install -r --offline
RUN pnpm run build
