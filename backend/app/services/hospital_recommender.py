import math
from typing import List, Optional, Dict, Any
from datetime import datetime


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    if max_val == min_val:
        return 1.0
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def recommend_hospitals(
    user_lat: float,
    user_lng: float,
    specialty: Optional[str] = None,
    urgency: str = "normal",
    hospitals: List[Dict[str, Any]],
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """
    Module 1 — Moteur de recommandation intelligent.

    Calcule un score de pertinence par hôpital à partir de:
      - distance GPS
      - temps d’attente estimé
      - qualité (rating)
      - disponibilité du service
      - urgence
    Retourne les max_results meilleurs établissements avec un score normalisé [0,1].
    """

    if not hospitals:
        return []

    scored: List[Dict[str, Any]] = []

    # Poids par urgence
    urgency_weights = {
        "critical": {"distance": 0.6, "rating": 0.1, "availability": 0.2, "waiting": 0.1},
        "urgent": {"distance": 0.4, "rating": 0.2, "availability": 0.25, "waiting": 0.15},
        "normal": {"distance": 0.25, "rating": 0.35, "availability": 0.2, "waiting": 0.2},
    }
    weights = urgency_weights.get(urgency, urgency_weights["normal"])

    distances = []
    ratings = []
    waiting_times = []

    for h in hospitals:
        lat = h.get("lat") or h.get("latitude")
        lng = h.get("lng") or h.get("longitude")
        if lat is None or lng is None:
            distances.append(50.0)
            ratings.append(3.0)
            waiting_times.append(60)
        else:
            distances.append(haversine_distance(user_lat, user_lng, float(lat), float(lng)))
            ratings.append(float(h.get("rating", 3.0)))
            waiting_times.append(float(h.get("average_waiting_time") or 60))

    min_dist, max_dist = min(distances), max(distances)
    min_rating, max_rating = min(ratings), max(ratings)
    min_wait, max_wait = min(waiting_times), max(waiting_times)

    for h, dist, rating, wait in zip(hospitals, distances, ratings, waiting_times):
        score_distance = normalize_score(dist, min_dist, max_dist)
        score_rating = normalize_score(rating, min_rating, max_rating)
        score_waiting = normalize_score(wait, min_wait, max_wait)

        services = h.get("services") or []
        service_match = 1.0 if (not specialty or specialty in services) else 0.3

        score = (
            weights["distance"] * score_distance
            + weights["rating"] * score_rating
            + weights["availability"] * service_match
            + weights["waiting"] * score_waiting
        )

        scored.append({
            "hospital": h,
            "score": round(score, 4),
            "distance_km": dist,
            "rating": rating,
            "estimated_waiting_minutes": int(wait),
            "specialty_match": service_match >= 0.9,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:max_results]
