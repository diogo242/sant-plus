# Déploiement — Santé+ prêt en 1 commande

## Lancement complet Docker
```bash
cp backend/.env.example backend/.env
docker compose up -d --build
```

## Vérifications
- Frontend : http://localhost:3000
- Backend : http://localhost:8000/docs
- Nginx : http://localhost

## Variables utiles
- `CORS_ORIGINS` pour publier le frontend ailleurs
- `DATABASE_URL` pour cibler une DB distante
- `JWT_SECRET_KEY` à changer en production
