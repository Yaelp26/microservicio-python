"""
Script para poblar la base de datos con datos de prueba
"""
import psycopg2
from datetime import datetime, timedelta
import random

# Configuración de conexión
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'booking_db',
    'user': 'booking_user',
    'password': 'booking_password'
}

# Datos de prueba
HOTELS = [1, 2, 3, 4, 5]
ROOM_TYPES = ['single', 'double', 'deluxe', 'suite', 'presidential']
STATUSES = ['confirmed', 'completed', 'cancelled', 'pending']


def create_sample_users(cursor):
    """Crear usuarios de prueba"""
    users = [
        ('Admin User', 'admin@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin'),
        ('John Doe', 'john@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'client'),
        ('Jane Smith', 'jane@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'client'),
        ('Bob Wilson', 'bob@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'client'),
        ('Alice Brown', 'alice@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'client'),
    ]
    
    for name, email, password, role in users:
        cursor.execute("""
            INSERT INTO users (name, email, password, role, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (email) DO NOTHING
        """, (name, email, password, role))
    
    print(f"✓ {len(users)} usuarios creados")


def create_sample_reservations(cursor, num_reservations=50):
    """Crear reservas de prueba"""
    cursor.execute("SELECT id FROM users WHERE role = 'client'")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    if not user_ids:
        print("⚠️ No hay usuarios clientes. Creando usuarios primero...")
        create_sample_users(cursor)
        cursor.execute("SELECT id FROM users WHERE role = 'client'")
        user_ids = [row[0] for row in cursor.fetchall()]
    
    created = 0
    today = datetime.now()
    
    for i in range(num_reservations):
        user_id = random.choice(user_ids)
        hotel_id = random.choice(HOTELS)
        room_type = random.choice(ROOM_TYPES)
        status = random.choice(STATUSES)
        
        # Generar fechas aleatorias
        days_offset = random.randint(-30, 60)
        check_in = today + timedelta(days=days_offset)
        check_out = check_in + timedelta(days=random.randint(1, 7))
        
        try:
            cursor.execute("""
                INSERT INTO reservations 
                (user_id, hotel_id, room_type, check_in, check_out, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (user_id, hotel_id, room_type, check_in, check_out, status))
            created += 1
        except Exception as e:
            print(f"Error al crear reserva {i+1}: {e}")
    
    print(f"✓ {created} reservas creadas")


def main():
    """Función principal"""
    print("🌱 Poblando base de datos con datos de prueba...")
    print("")
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✓ Conectado a la base de datos")
        
        # Crear usuarios
        print("\n📝 Creando usuarios...")
        create_sample_users(cursor)
        
        # Crear reservas
        print("\n📅 Creando reservas...")
        create_sample_reservations(cursor, num_reservations=100)
        
        # Commit de los cambios
        conn.commit()
        
        # Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM reservations")
        reservation_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) FROM reservations GROUP BY status")
        status_counts = cursor.fetchall()
        
        print("\n" + "="*50)
        print("✅ Datos de prueba creados exitosamente!")
        print("="*50)
        print(f"\n📊 Resumen:")
        print(f"  • Total usuarios: {user_count}")
        print(f"  • Total reservas: {reservation_count}")
        print(f"\n  Reservas por estado:")
        for status, count in status_counts:
            print(f"    - {status}: {count}")
        
        print("\n🔗 URLs para probar:")
        print("  • API Analytics: http://localhost:8000/analytics/occupancy")
        print("  • Swagger Docs:  http://localhost:8000/docs")
        print("")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Error de conexión a la base de datos:")
        print(f"   {e}")
        print("\n💡 Asegúrate de que:")
        print("   1. Los servicios están corriendo (./start-services.sh)")
        print("   2. PostgreSQL está disponible en localhost:5432")
        print("   3. Las credenciales en DB_CONFIG son correctas")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    main()
