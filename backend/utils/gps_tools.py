from datetime import datetime, timedelta
from math import radians, cos, sin, sqrt, atan2, asin, degrees
from typing import Tuple, Optional, Dict, List
from sqlalchemy.orm import Session

from backend.models import (
    stop as stop_model,
    run as run_model,
    student as student_model,
    associations as assoc_model,
)


def validate_gps(lat: float, lng: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lng <= 180


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lng2 - lng1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def simulate_gps_position(
    start_lat: float, start_lng: float, bearing: float, speed_kmh: float, seconds: int
) -> Tuple[float, float]:
    distance_m = (speed_kmh * 1000 / 3600) * seconds
    r = 6371000
    bearing_rad = radians(bearing)

    lat1 = radians(start_lat)
    lng1 = radians(start_lng)

    lat2 = asin(
        sin(lat1) * cos(distance_m / r)
        + cos(lat1) * sin(distance_m / r) * cos(bearing_rad)
    )
    lng2 = lng1 + atan2(
        sin(bearing_rad) * sin(distance_m / r) * cos(lat1),
        cos(distance_m / r) - sin(lat1) * sin(lat2),
    )

    return round(degrees(lat2), 6), round(degrees(lng2), 6)


def is_bus_approaching(
    bus_lat: float,
    bus_lng: float,
    target_lat: float,
    target_lng: float,
    threshold_meters: float = 500,
) -> bool:
    if not validate_gps(bus_lat, bus_lng) or not validate_gps(target_lat, target_lng):
        return False
    distance = haversine_distance(bus_lat, bus_lng, target_lat, target_lng)
    return distance <= threshold_meters


def get_current_stop_progress(
    db: Session, run_id: int, current_lat: float, current_lng: float
) -> Dict:
    run = db.get(run_model.Run, run_id)
    if not run:
        return {"error": "Run not found"}

    stops = sorted(run.stops, key=lambda s: s.sequence)
    if not stops:
        return {"error": "No stops on run"}

    valid_stops = [
        stop
        for stop in stops
        if stop.latitude is not None and stop.longitude is not None
    ]
    if not valid_stops:
        return {"error": "No GPS-enabled stops"}

    distances = [
        (
            stop,
            haversine_distance(current_lat, current_lng, stop.latitude, stop.longitude),
        )
        for stop in valid_stops
    ]
    current_stop, _ = min(distances, key=lambda x: x[1])
    current_idx = stops.index(current_stop)

    next_stop = stops[current_idx + 1] if current_idx + 1 < len(stops) else None

    progress = 0.0
    if next_stop and next_stop.latitude is not None:
        total = haversine_distance(
            current_stop.latitude,
            current_stop.longitude,
            next_stop.latitude,
            next_stop.longitude,
        )
        remaining = haversine_distance(
            current_lat, current_lng, next_stop.latitude, next_stop.longitude
        )
        if total > 0:
            progress = max(0, min(100, ((total - remaining) / total) * 100))

    return {
        "current_stop": {
            "id": current_stop.id,
            "sequence": current_stop.sequence,
            "type": (
                current_stop.type.value
                if hasattr(current_stop.type, "value")
                else str(current_stop.type)
            ),
            "name": current_stop.name or f"Stop {current_stop.sequence}",
        },
        "next_stop": (
            {
                "id": next_stop.id,
                "sequence": next_stop.sequence,
                "name": next_stop.name or "End of Run",
            }
            if next_stop
            else None
        ),
        "progress_percent": round(progress, 1),
        "total_stops": len(stops),
    }


def estimate_eta(
    db: Session,
    run_id: int,
    current_lat: float,
    current_lng: float,
    avg_speed_kmh: float = 30,
) -> Optional[datetime]:
    progress = get_current_stop_progress(db, run_id, current_lat, current_lng)
    if "error" in progress or not progress.get("next_stop"):
        return None

    next_stop_id = progress["next_stop"]["id"]
    next_stop = db.get(stop_model.Stop, next_stop_id)
    if not next_stop or next_stop.latitude is None:
        return None

    distance_m = haversine_distance(
        current_lat, current_lng, next_stop.latitude, next_stop.longitude
    )
    minutes = distance_m / (avg_speed_kmh * 1000 / 60)
    return datetime.now() + timedelta(minutes=minutes)


def get_approaching_alerts(
    db: Session, run_id: int, bus_lat: float, bus_lng: float
) -> List[Dict]:
    progress = get_current_stop_progress(db, run_id, bus_lat, bus_lng)
    if "error" in progress or not progress.get("next_stop"):
        return []

    next_stop = db.get(stop_model.Stop, progress["next_stop"]["id"])
    if not next_stop or next_stop.latitude is None:
        return []

    assignments = (
        db.query(assoc_model.StudentRunAssignment)
        .filter(assoc_model.StudentRunAssignment.run_id == run_id)
        .filter(assoc_model.StudentRunAssignment.stop_id == next_stop.id)
        .all()
    )

    alerts = []
    for assignment in assignments:
        student = db.get(student_model.Student, assignment.student_id)
        if not student:
            continue

        threshold = student.notification_distance_meters or 500
        if is_bus_approaching(
            bus_lat, bus_lng, next_stop.latitude, next_stop.longitude, threshold
        ):
            eta = estimate_eta(db, run_id, bus_lat, bus_lng)
            eta_str = eta.strftime("%I:%M %p") if eta else "soon"

            alerts.append(
                {
                    "student_id": student.id,
                    "student_name": student.name,
                    "message": f"Bus is approaching your stop! ETA: {eta_str}",
                    "distance_meters": round(
                        haversine_distance(
                            bus_lat, bus_lng, next_stop.latitude, next_stop.longitude
                        ),
                        1,
                    ),
                    "stop_name": next_stop.name or f"Stop {next_stop.sequence}",
                }
            )
    return alerts
