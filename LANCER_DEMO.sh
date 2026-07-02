#!/bin/bash
# =============================================================================
# SANTÉ PLUS - LANCEMENT AUTOMATIQUE
# Backend Python + Frontend React
# =============================================================================

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   🚀 SANTÉ PLUS - LANCEMENT AUTOMATIQUE       ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Backend
echo "🐍 Démarrage Backend Python (port 8000)..."
cd "/home/ahilihan/Téléchargements/santeplus1/backend"
python3 main.py &
BACKEND_PID=$!

sleep 3

# Frontend
echo "⚛️  Démarrage Frontend React (port 3000)..."
echo ""
cd "/home/ahilihan/Téléchargements/santeplus1"
npm run dev &
FRONTEND_PID=$!

# Résumé
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   ✅  SANTÉ PLUS PRÊT !                       ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "📱 Frontend : http://localhost:3000"
echo "🔧 Backend  : http://localhost:8000"
echo "📚 API Docs : http://localhost:8000/docs"
echo ""
echo "🔐 Compte :"
echo "   Email    : bienvenuesegnon@gmail.com"
echo "   Password : (aucun)"
echo ""
echo "💡 Fonctionnalités :"
echo "   • Carte interactive 5 hôpitaux"
echo "   • Prise de rendez-vous"
echo "   • Documents médicaux"
echo "   • Paiement Lightning"
echo ""
echo "🎯 Bonne présentation !"
echo ""

wait
