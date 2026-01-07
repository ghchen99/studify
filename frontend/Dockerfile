# =========================
# Base
# =========================
FROM node:24-alpine AS base
WORKDIR /app

# =========================
# Dependencies
# =========================
FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

# =========================
# Build
# =========================
FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# =========================
# Runtime
# =========================
FROM node:24-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=8080

# Copy only what Next.js needs at runtime
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/next.config.* ./
COPY --from=build /app/next-env.d.ts ./next-env.d.ts

EXPOSE 8080
CMD ["npm", "run", "start"]
