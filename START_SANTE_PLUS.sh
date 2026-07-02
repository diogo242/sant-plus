#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WORKSPACE="/home/ahilihan/Téléchargements/santeplus1"
BACKEND_DIR="$WORKSPACE/backend"
LOG_DIR="$WORKSPACE/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

mkdir -p "$LOG_DIR"

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   🚀 SANTÉ+ — LANCEMENT PROFESSIONNEL        ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Nettoyage des ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 1

# Backend
echo -e "${GREEN}[1/2]${NC} 🐍 Backend FastAPI"
cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
  echo -e "${YELLOW}📦 Premier lancement : installation du venv...${NC}"
  python3 -m venv .venv
  "$BACKEND_DIR/.venv/bin/pip" install --upgrade pip
  "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
  "$BACKEND_DIR/.venv/bin/pip" install asyncpg
else
  echo -e "${BLUE}✅ venv détecté${NC}"
fi

cd "$WORKSPACE"
echo -e "${BLUE}🚀 Démarrage backend sur http://0.0.0.0:8000${NC}"
PYTHONPATH="$WORKSPACE" "$BACKEND_DIR/.venv/bin/uvicorn" "backend.main:app" --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

# Frontend
echo -e "${GREEN}[2/2]${NC} ⚛️  Frontend React"
cd "$WORKSPACE"

if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}📦 npm install requis...${NC}"
  npm install
else
  echo -e "${BLUE}✅ node_modules présent${NC}"
fi

echo -e "${BLUE}🚀 npm run dev sur http://localhost:3000${NC}"
npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

sleep 6

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   ✅  SANTÉ+ PRÊT — DÉMO INVESTISSEURS       ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo -e "📱 Frontend : ${BLUE}http://localhost:3000${NC}"
echo -e "🔧 Backend  : ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "👤 COMPTES DÉMO :"
echo "   Patient  : bienvenuesegnon@gmail.com / 123456"
echo "   Agent     : agent.sante@sante.bj / agent123"
echo ""
echo "🎯 FLUX DÉMO :"
echo "   1. Créer un compte patient"
echo "   2. Ouvrir le dossier médical chiffré"
echo "   3. Partager le code d'accès"
echo "   4. Se connecter en tant qu'agent"
echo "   5. Ajouter une mise à jour confirmée"
echo "   6. Vérifier les changements côté patient"
echo "   7. Payer la facture en Bitcoin/Lightning"
echo ""
echo -e "${YELLOW}Logs :${NC}"
echo "   Backend : $BACKEND_LOG"
echo "   Frontend: $FRONTEND_LOG"
echo ""
echo -e "${YELLOW}Arrêt :${NC} Ctrl+C"
echo ""

wait
