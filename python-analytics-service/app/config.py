"""
Configuración del servicio de analytics
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Database
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "booking_db"
    db_user: str = "booking_user"
    db_password: str = "booking_password"
    
    # RabbitMQ
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_queue: str = "analytics_queue"
    
    # JWT
    jwt_secret: str = "7rTsLU4hJE0X80Wau2EYeBL6vp0pg1VWhy7mi7PvXuMozvUelbRFnpGA2yMq2t0A"
    jwt_algorithm: str = "HS256"
    jwt_iss: str = "travelink-laravel"
    jwt_aud: str = "travelink-api"
    
    # Service
    service_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    """Obtener configuración singleton"""
    return Settings()
