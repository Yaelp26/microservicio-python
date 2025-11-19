from fastapi import APIRouter

router = APIRouter()

@router.get("/occupancy")
def get_occupancy():
    # En el futuro: consulta real a BD (PostgreSQL)
    return {
        "total_reservations": 42,
        "occupied_rooms": 30,
        "occupancy_rate": "71%"
    }
