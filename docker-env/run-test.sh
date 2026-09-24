#!/usr/bin/env bash
# ==========================================================================
# run-test.sh — wrapper WAJIB untuk SEMUA eksekusi test G1/Step 9 lewat Docker
# (diinstansiasi dari migration-tool/templates/run-test.sh.template, 2026-09-24,
#  appointment_jitsi 19.0 -> 20.0)
# ==========================================================================
# KENAPA FILE INI ADA (jangan hapus catatan ini):
# 1. `--test-tags /<module>` rawan di-mangle MSYS/Git Bash jadi path Windows ->
#    tag filter kosong -> "0 failed, 0 error(s) of 0 tests" (false-pass).
#    Wrapper ini hardcode MSYS_NO_PATHCONV=1.
# 2. DB yang sudah pernah `-i` membuat install+test diam-diam di-skip (false-pass
#    identik). Wrapper ini SELALU `docker compose down -v` dulu.
# Sanity-check: jumlah baris "Starting <Class>.<method>" harus > 0 (dan dicocokkan
# manual ke jumlah test yang diharapkan).
#
# USAGE (dari folder docker-env/):
#   ./run-test.sh <service> <db_name> <module_name> [tag_tambahan]
# CONTOH:
#   ./run-test.sh odoo appointment_jitsi_test_20 appointment_jitsi
# ==========================================================================
set -euo pipefail

export COMPOSE_FILE="docker-compose.20.0.yml"

SERVICE="${1:?Usage: run-test.sh <service> <db_name> <module_name> [extra_tags]}"
DB_NAME="${2:?Usage: run-test.sh <service> <db_name> <module_name> [extra_tags]}"
MODULE_NAME="${3:?Usage: run-test.sh <service> <db_name> <module_name> [extra_tags]}"
EXTRA_TAGS="${4:-}"

TAGS="/${MODULE_NAME}${EXTRA_TAGS}"
mkdir -p logs
LOGFILE="logs/run-test-$(date +%Y%m%d-%H%M%S).log"
ADDONS_PATH="/opt/odoo/addons,/opt/odoo/odoo/addons,/mnt/enterprise,/mnt/extra-addons"

echo "=== run-test.sh: MSYS_NO_PATHCONV=1 + fresh DB (down -v) setiap run ==="
echo "=== compose=${COMPOSE_FILE} service=${SERVICE} db=${DB_NAME} module=${MODULE_NAME} tags=${TAGS} ==="
echo "=== log lengkap: docker-env/${LOGFILE} ==="

docker compose down -v 2>&1 | tail -5

MSYS_NO_PATHCONV=1 docker compose run --rm "${SERVICE}" \
  -d "${DB_NAME}" -i "${MODULE_NAME}" --without-demo=all \
  --addons-path="${ADDONS_PATH}" \
  --test-enable --test-tags "${TAGS}" --stop-after-init 2>&1 | tee "${LOGFILE}" || true

echo ""
echo "=== Sanity check otomatis ==="
STARTED_COUNT=$(grep -c "Starting " "${LOGFILE}" || true)
SUMMARY_LINE=$(grep -E "[0-9]+ failed, [0-9]+ error\(s\) of [0-9]+ tests" "${LOGFILE}" | tail -1 || true)
ERROR_COUNT=$(grep -cE " (ERROR|CRITICAL) " "${LOGFILE}" || true)
echo "Baris 'Starting <Class>.<method>': ${STARTED_COUNT}"
echo "Baris ERROR/CRITICAL di log: ${ERROR_COUNT}"
echo "Ringkasan Odoo: ${SUMMARY_LINE:-'(tidak ditemukan)'}"

docker compose down -v 2>&1 | tail -5

if [ "${STARTED_COUNT}" -eq 0 ]; then
  echo "GAGAL — 0 test ter-start (false-pass / install gagal). Buka docker-env/${LOGFILE}."
  exit 2
fi
echo "OK — ${STARTED_COUNT} test method ter-eksekusi."
