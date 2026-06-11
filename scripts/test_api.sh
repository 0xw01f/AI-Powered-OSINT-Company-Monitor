#!/usr/bin/env bash
# Quick smoke-test for the OSINT Monitor API.
# Usage: bash scripts/test_api.sh [PORT]
# Default port is 8001 (use 8000 if you started the server on the default port).

set -euo pipefail

PORT="${1:-8001}"
BASE="http://127.0.0.1:${PORT}"

echo "=== OSINT Monitor API Smoke Test ==="
echo "Base URL: ${BASE}"
echo ""

# 1. Health
echo "→ GET /health"
curl -sf "${BASE}/health" | python -m json.tool
echo ""

# 2. Sources (top 3 by priority)
echo "→ GET /sources/?active_only=true&min_priority=95&limit=3"
curl -sf "${BASE}/sources/?active_only=true&min_priority=95&limit=3" | python -m json.tool
echo ""

# 3. RSS collection (small batch)
echo "→ POST /collect/rss?max_sources=3&limit_per_source=2"
curl -sf -X POST "${BASE}/collect/rss?max_sources=3&limit_per_source=2" | python -m json.tool
echo ""

# 4. Scheduler status
echo "→ GET /collect/scheduler/status"
curl -sf "${BASE}/collect/scheduler/status" | python -m json.tool
echo ""

# 5. Watchlist: add a company
echo "→ POST /collect/monitor/watch?name=Apple"
curl -sf -X POST "${BASE}/collect/monitor/watch?name=Apple" | python -m json.tool
echo ""

# 6. Watchlist: list
echo "→ GET /collect/monitor/watched"
curl -sf "${BASE}/collect/monitor/watched" | python -m json.tool
echo ""

# 7. Search articles
echo "→ GET /collect/monitor/search?name=Apple&limit=5"
curl -sf "${BASE}/collect/monitor/search?name=Apple&limit=5" | python -m json.tool
echo ""

# 8. Benchmark NER
echo "→ POST /collect/benchmark"
curl -sf -X POST "${BASE}/collect/benchmark?text=Apple%20Inc.%20announced%20a%20partnership%20with%20OpenAI%20in%20San%20Francisco.&language=en" | python -m json.tool
echo ""

echo "=== All smoke tests passed ==="
