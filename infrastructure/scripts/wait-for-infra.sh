#!/usr/bin/env bash
# Wait for Postgres and Redis health before starting dependent processes.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Waiting for Postgres and Redis..."
for i in {1..30}; do
  if docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-praevis}" >/dev/null 2>&1 \
    && docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "Infrastructure is ready."
    exit 0
  fi
  sleep 1
done

echo "Timed out waiting for infrastructure." >&2
exit 1
