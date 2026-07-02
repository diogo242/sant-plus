#!/bin/bash
set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WORKSPACE="/home/ahilihan/Téléchargements/santeplus1"
BACKEND_DIR="$WORKSPACE/backend"

echo ""
echo -e "${GREEN}🐍 Lancement Backend Santé+${NC}"
echo ""

cd "$BACKEND_DIR"

command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ python3 introuvable${NC}"; exit 1; }

if [ ! -d ".venv" ]; then
  echo -e "${YELLOW}📦 Création du venv et install des dépendances...${NC}"
  python3 -m venv .venv
  "$BACKEND_DIR/.venv/bin/python" -m pip install --upgrade pip
  "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
else
  echo -e "${BLUE}✅ venv existant détecté${NC}"
fi

echo -e "${YELLOW}🔧 Installation de asyncpg si besoin...${NC}"
"$BACKEND_DIR/.venv/bin/pip" install asyncpg || true

cd "$WORKSPACE"
echo -e "${BLUE}🚀 Démarrage uvicorn sur http://0.0.0.0:8000${NC}"
echo -e "${YELLOW}ℹ️  Arrêt avec Ctrl+C${NC}"
echo ""

exec "$BACKEND_DIR/.venv/bin/uvicorn" "backend.main:app" --host 0.0.0.0 --port 8000 --reload
