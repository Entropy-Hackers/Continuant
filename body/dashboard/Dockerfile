# Stage 1: build the Vue 3 frontend (Vite) into static assets.
FROM node:22-slim AS frontend-build
WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: the FastAPI backend, serving both /api/* and the built frontend.
# No Node runtime in the final image — just the static dist/ output.
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=frontend-build /app/dist ./frontend_dist

# Runs as a non-root, fixed UID/GID — matches the group audit-tap and
# control-exec's host-side directories are chowned to (root:10001, see
# tools/*/README.md); the ONLY directory this user may write to is
# control/ (rw-mounted), everything else (audit/, workspace/) stays ro.
RUN useradd --create-home --uid 10001 dashboard
USER dashboard

EXPOSE 8090
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090", "--workers", "1"]
