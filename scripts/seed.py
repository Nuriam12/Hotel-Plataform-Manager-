"""
Seed script — pobla la base de datos con datos iniciales para desarrollo.

Idempotente: si el hotel "Hotel Demo" ya existe, no crea duplicados.

Uso:
    python -m scripts.seed
    # o desde la raíz del proyecto:
    python scripts/seed.py
"""

import asyncio
import sys
from pathlib import Path

# Añadir el raíz del proyecto al path para poder importar los módulos de app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.models.hotel import Hotel
from app.models.inventory_product import InventoryProduct
from app.models.room import Room
from app.models.user import User

# ---------------------------------------------------------------------------
# Datos iniciales
# ---------------------------------------------------------------------------

HOTEL_NAME = "Hotel Demo"

ADMIN_USER = {
    "username": "admin",
    "password": "admin123",
    "role": "ADMINISTRADOR",
    "shift": "mañana",
}

STAFF_USERS = [
    {"username": "trabajador1", "password": "staff123", "role": "TRABAJADOR", "shift": "mañana"},
    {"username": "trabajador2", "password": "staff123", "role": "TRABAJADOR", "shift": "tarde"},
]

ROOMS = [
    {"room_number": "101", "floor": "1", "room_type": "individual", "price_per_night": 50},
    {"room_number": "102", "floor": "1", "room_type": "doble", "price_per_night": 80},
    {"room_number": "103", "floor": "1", "room_type": "doble", "price_per_night": 80},
    {"room_number": "201", "floor": "2", "room_type": "suite", "price_per_night": 150},
    {"room_number": "202", "floor": "2", "room_type": "individual", "price_per_night": 50},
    {"room_number": "203", "floor": "2", "room_type": "doble", "price_per_night": 80},
]

PRODUCTS = [
    {"name": "Agua mineral 500ml", "category": "bebidas", "price": 2.50},
    {"name": "Cerveza lata", "category": "bebidas", "price": 4.00},
    {"name": "Gaseosa lata", "category": "bebidas", "price": 3.00},
    {"name": "Café", "category": "bebidas", "price": 2.00},
    {"name": "Snack papas fritas", "category": "snacks", "price": 3.50},
    {"name": "Chocolatina", "category": "snacks", "price": 2.50},
    {"name": "Toalla extra", "category": "servicios", "price": 5.00},
    {"name": "Servicio lavandería", "category": "servicios", "price": 15.00},
]


# ---------------------------------------------------------------------------
# Lógica de seed
# ---------------------------------------------------------------------------

async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # --- Hotel ---
        result = await db.execute(select(Hotel).where(Hotel.name == HOTEL_NAME))
        hotel = result.scalar_one_or_none()

        if hotel is None:
            hotel = Hotel(name=HOTEL_NAME, address="Calle Principal 1", phone="555-0000")
            db.add(hotel)
            await db.flush()
            print(f"[+] Hotel creado: {hotel.name} (id={hotel.id})")
        else:
            print(f"[=] Hotel ya existe: {hotel.name} (id={hotel.id})")

        # --- Usuario Admin ---
        result = await db.execute(
            select(User).where(User.hotel_id == hotel.id, User.username == ADMIN_USER["username"])
        )
        if result.scalar_one_or_none() is None:
            db.add(User(
                hotel_id=hotel.id,
                username=ADMIN_USER["username"],
                password_hash=hash_password(ADMIN_USER["password"]),
                role=ADMIN_USER["role"],
                shift=ADMIN_USER["shift"],
            ))
            print(f"[+] Usuario admin creado: {ADMIN_USER['username']}")
        else:
            print(f"[=] Usuario admin ya existe: {ADMIN_USER['username']}")

        # --- Usuarios Trabajadores ---
        for staff in STAFF_USERS:
            result = await db.execute(
                select(User).where(User.hotel_id == hotel.id, User.username == staff["username"])
            )
            if result.scalar_one_or_none() is None:
                db.add(User(
                    hotel_id=hotel.id,
                    username=staff["username"],
                    password_hash=hash_password(staff["password"]),
                    role=staff["role"],
                    shift=staff["shift"],
                ))
                print(f"[+] Trabajador creado: {staff['username']}")
            else:
                print(f"[=] Trabajador ya existe: {staff['username']}")

        # --- Habitaciones ---
        for r in ROOMS:
            result = await db.execute(
                select(Room).where(Room.hotel_id == hotel.id, Room.room_number == r["room_number"])
            )
            if result.scalar_one_or_none() is None:
                db.add(Room(
                    hotel_id=hotel.id,
                    room_number=r["room_number"],
                    floor=r["floor"],
                    room_type=r["room_type"],
                    price_per_night=r["price_per_night"],
                    status="available",
                ))
                print(f"[+] Habitación creada: {r['room_number']}")
            else:
                print(f"[=] Habitación ya existe: {r['room_number']}")

        # --- Productos de inventario ---
        for p in PRODUCTS:
            result = await db.execute(
                select(InventoryProduct).where(
                    InventoryProduct.hotel_id == hotel.id,
                    InventoryProduct.name == p["name"],
                )
            )
            if result.scalar_one_or_none() is None:
                db.add(InventoryProduct(
                    hotel_id=hotel.id,
                    name=p["name"],
                    category=p["category"],
                    price=p["price"],
                    current_stock=0,
                ))
                print(f"[+] Producto creado: {p['name']}")
            else:
                print(f"[=] Producto ya existe: {p['name']}")

        await db.commit()
        print("\n✓ Seed completado.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
