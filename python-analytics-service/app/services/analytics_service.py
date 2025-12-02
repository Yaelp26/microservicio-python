"""
Servicio de analytics para generar estadísticas de ocupación
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models import Reservation
from app.schemas import OccupancyStats
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Servicio para generar estadísticas de ocupación"""
    
    @staticmethod
    def get_occupancy_statistics(db: Session) -> OccupancyStats:
        """
        Genera estadísticas de ocupación basadas en las reservas
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            OccupancyStats con las estadísticas calculadas
        """
        try:
            # Contar total de reservaciones
            total_reservations = db.query(func.count(Reservation.id)).scalar()
            
            # Contar por estado
            active_reservations = db.query(func.count(Reservation.id))\
                .filter(Reservation.status == 'confirmed').scalar() or 0
                
            completed_reservations = db.query(func.count(Reservation.id))\
                .filter(Reservation.status == 'completed').scalar() or 0
                
            cancelled_reservations = db.query(func.count(Reservation.id))\
                .filter(Reservation.status == 'cancelled').scalar() or 0
            
            # Calcular tasa de ocupación
            occupancy_rate = 0.0
            if total_reservations > 0:
                occupancy_rate = round((active_reservations / total_reservations) * 100, 2)
            
            # Estadísticas por hotel
            by_hotel = db.query(
                Reservation.hotel_id,
                func.count(Reservation.id).label('count'),
                func.count(case((Reservation.status == 'confirmed', 1))).label('active')
            ).group_by(Reservation.hotel_id).all()
            
            by_hotel_list = [
                {
                    'hotel_id': h.hotel_id,
                    'total_reservations': h.count,
                    'active_reservations': h.active,
                    'occupancy_rate': round((h.active / h.count * 100), 2) if h.count > 0 else 0
                }
                for h in by_hotel
            ]
            
            # Estadísticas por tipo de habitación
            by_room_type = db.query(
                Reservation.room_type,
                func.count(Reservation.id).label('count'),
                func.count(case((Reservation.status == 'confirmed', 1))).label('active')
            ).group_by(Reservation.room_type).all()
            
            by_room_type_list = [
                {
                    'room_type': r.room_type,
                    'total_reservations': r.count,
                    'active_reservations': r.active
                }
                for r in by_room_type
            ]
            
            # Estadísticas por estado
            by_status = db.query(
                Reservation.status,
                func.count(Reservation.id).label('count')
            ).group_by(Reservation.status).all()
            
            by_status_list = [
                {
                    'status': s.status,
                    'count': s.count,
                    'percentage': round((s.count / total_reservations * 100), 2) if total_reservations > 0 else 0
                }
                for s in by_status
            ]
            
            logger.info(f"Estadísticas generadas: {total_reservations} reservaciones totales")
            
            return OccupancyStats(
                total_reservations=total_reservations or 0,
                active_reservations=active_reservations,
                completed_reservations=completed_reservations,
                cancelled_reservations=cancelled_reservations,
                occupancy_rate=occupancy_rate,
                by_hotel=by_hotel_list,
                by_room_type=by_room_type_list,
                by_status=by_status_list
            )
            
        except Exception as e:
            logger.error(f"Error al generar estadísticas: {e}")
            raise
