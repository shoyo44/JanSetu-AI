# ── Stage 1: Build Frontend Assets ──────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code and build production bundle
COPY . .
RUN npm run build

# ── Stage 2: Serve via Hardened Nginx ────────────────────────────────────────
FROM nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy hardened nginx configuration with security headers
COPY nginx.conf /etc/nginx/conf.d/

# Copy built frontend assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
