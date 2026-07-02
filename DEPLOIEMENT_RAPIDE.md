# 🚀 DÉPLOIEMENT RAPIDE

## ⚡ EN 5 MINUTES

---

## 📋 PRÉREQUIS

- Compte GitHub
- Compte Railway.app (backend)
- Compte Vercel.com (frontend)

---

## 🎯 BACKEND PYTHON (2 min)

1. Pousse le code sur GitHub
2. Va sur https://railway.app
3. "New Project" → "Deploy from GitHub"
4. Sélectionne ton repo
5. Railway détecte FastAPI automatiquement
6. Clique "Deploy"

**Résultat :** https://santeplus-backend.railway.app

---

## 🎯 FRONTEND REACT (2 min)

1. Va sur https://vercel.com
2. "Import Project" → GitHub
3. Root Directory : `/`
4. Build : `npm run build`
5. Output : `dist`
6. Clique "Deploy"

**Résultat :** https://santeplus.vercel.app

---

## 🎯 CONNECTER (1 min)

Dans le frontend, créer `.env.production` :
```env
VITE_API_URL=https://santeplus-backend.railway.app
```

Rebuild et redeploy sur Vercel.

---

## ✅ C'EST PRÊT !

Application déployée publiquement !
