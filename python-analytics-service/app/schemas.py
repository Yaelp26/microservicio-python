"""
Esquemas Pydantic para validación de datos
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OccupancyStats(BaseModel):
    """Estadísticas de ocupación"""
    total_reservations: int = Field(..., description="Total de reservaciones")
    active_reservations: int = Field(..., description="Reservaciones activas")
    completed_reservations: int = Field(..., description="Reservaciones completadas")
    cancelled_reservations: int = Field(..., description="Reservaciones canceladas")
    occupancy_rate: float = Field(..., description="Tasa de ocupación (%)")
    by_hotel: List[dict] = Field(..., description="Estadísticas por hotel")
    by_room_type: List[dict] = Field(..., description="Estadísticas por tipo de habitación")
    by_status: List[dict] = Field(..., description="Estadísticas por estado")


class OccupancyResponse(BaseModel):
    """Respuesta del endpoint de ocupación"""
    success: bool
    message: str
    data: Optional[OccupancyStats] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Respuesta de error"""
    success: bool = False
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
