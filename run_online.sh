#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# BASA ENTERPRISE SAAS SUITE - LAUNCHER 100% ONLINE (VPS / CLOUD / DOCKER)
# Autor: Lic. Pedro Baldera (licpedrobaldera@gmail.com)
# =============================================================================

APP_FILE="basa_enterprise_suite.py"
PORT="${PORT:-8501}"

if [ ! -f "$APP_FILE" ]; then
  echo "Error: No se encuentra $APP_FILE en el directorio actual."
  exit 1
fi

echo "[1/3] Configurando Streamlit para despliegue en línea (puerto $PORT)..."
mkdir -p .streamlit
cat > .streamlit/config.toml <<EOF
[server]
headless = true
address = "0.0.0.0"
port = ${PORT}
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
EOF

echo "[2/3] Instalando dependencias..."
python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
python3 -m pip install streamlit pandas reportlab requests psycopg2-binary cryptography lxml signxml

echo "[3/3] Iniciando BASA Enterprise SaaS Suite en http://0.0.0.0:${PORT} ..."
exec streamlit run "$APP_FILE" --server.port="$PORT" --server.address="0.0.0.0"
