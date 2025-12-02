"""
API Principal del servicio de Analytics
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import OccupancyResponse, ErrorResponse
from app.services.analytics_service import AnalyticsService
from app.rabbitmq import rabbitmq_client
from app.config import get_settings
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración
settings = get_settings()

# Crear aplicación FastAPI
app = FastAPI(
    title="Analytics Service",
    description="Servicio de análisis y estadísticas de ocupación para sistema de reservas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    logger.info("Iniciando servicio de Analytics...")
    try:
        # Conectar a RabbitMQ
        rabbitmq_client.connect()
        logger.info("Conexión a RabbitMQ establecida")
    except Exception as e:
        logger.error(f"Error al conectar con RabbitMQ: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento al cerrar la aplicación"""
    logger.info("Cerrando servicio de Analytics...")
    rabbitmq_client.close()


@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz para verificar que el servicio está activo"""
    return {
        "service": "Analytics Service",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get(
    "/analytics/occupancy",
    response_model=OccupancyResponse,
    responses={
        200: {"description": "Estadísticas obtenidas exitosamente"},
        500: {"model": ErrorResponse, "description": "Error del servidor"}
    },
    tags=["Analytics"]
)
async def get_occupancy_statistics(db: Session = Depends(get_db)):
    """
    Obtener estadísticas de ocupación
    
    Este endpoint procesa la información de la base de datos de reservas
    y genera estadísticas detalladas de ocupación.
    
    **Flujo:**
    1. El admin envía GET /analytics/occupancy
    2. Python procesa la información de la base de datos
    3. Genera estadísticas de ocupación
    4. Devuelve los resultados al cliente
    
    **Actores:** Admin, Servicio Python (Analytics)
    
    Returns:
        OccupancyResponse con las estadísticas de ocupación
    """
    try:
        logger.info("Solicitando estadísticas de ocupación...")
        
        # Generar estadísticas
        analytics_service = AnalyticsService()
        stats = analytics_service.get_occupancy_statistics(db)
        
        # Publicar evento en RabbitMQ
        try:
            message = {
                "event": "occupancy_stats_generated",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "total_reservations": stats.total_reservations,
                    "active_reservations": stats.active_reservations,
                    "occupancy_rate": stats.occupancy_rate
                }
            }
            rabbitmq_client.publish_message(message)
        except Exception as e:
            logger.error(f"Error crítico al publicar en RabbitMQ: {e}", exc_info=True)
        
        logger.info("Estadísticas generadas exitosamente")
        
        return OccupancyResponse(
            success=True,
            message="Estadísticas de ocupación obtenidas exitosamente",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Error al generar estadísticas",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/analytics/occupancy/hotel/{hotel_id}", tags=["Analytics"])
async def get_hotel_occupancy(hotel_id: int, db: Session = Depends(get_db)):
    """
    Obtener estadísticas de ocupación de un hotel específico
    
    Args:
        hotel_id: ID del hotel
        
    Returns:
        Estadísticas específicas del hotel
    """
    try:
        from sqlalchemy import func, case
        from app.models import Reservation
        
        # Consultar reservas del hotel
        total = db.query(func.count(Reservation.id))\
            .filter(Reservation.hotel_id == hotel_id).scalar() or 0
        
        active = db.query(func.count(Reservation.id))\
            .filter(Reservation.hotel_id == hotel_id)\
            .filter(Reservation.status == 'confirmed').scalar() or 0
        
        occupancy_rate = round((active / total * 100), 2) if total > 0 else 0
        
        return {
            "success": True,
            "data": {
                "hotel_id": hotel_id,
                "total_reservations": total,
                "active_reservations": active,
                "occupancy_rate": occupancy_rate
            }
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del hotel: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
