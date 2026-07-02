#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WORKSPACE="/home/ahilihan/Téléchargements/santeplus1"

echo ""
echo -e "${GREEN}⚛️  Lancement Frontend Santé+${NC}"
echo ""

cd "$WORKSPACE"

command -v node >/dev/null 2>&1 || { echo -e "${RED}❌ node introuvable${NC}"; exit 1; }

if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}📦 npm install...${NC}"
  npm install
else
  echo -e "${BLUE}✅ node_modules présent, pas de réinstall complet${NC}"
fi

echo -e "${BLUE}🚀 npm run dev sur http://localhost:3000${NC}"
echo -e "${YELLOW}ℹ️  Arrêt avec Ctrl+C${NC}"
echo ""

npm run dev
