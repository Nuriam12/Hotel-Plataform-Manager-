from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import Reservation
from app.repositories.client_repository import ClientRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.reservation import ReservationCreate


class ReservationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.reservation_repository = ReservationRepository(db)
        self.room_repository = RoomRepository(db)
        self.client_repository = ClientRepository(db)

    async def create(
        self,
        hotel_id: int,
        user_id: int,
        data: ReservationCreate,
    ) -> Reservation:
        room = await self.room_repository.get_by_id_and_hotel(
            hotel_id, data.room_id
        )
        if room is None:
            raise LookupError("La habitación no existe en este hotel.")

        client = await self.client_repository.get_by_id_and_hotel(
            hotel_id, data.client_id
        )
        if client is None:
            raise LookupError("El cliente no existe en este hotel.")

        overlap = await self.reservation_repository.has_overlapping_reservation(
            hotel_id=hotel_id,
            room_id=data.room_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        if overlap:
            raise ValueError(
                "La habitación ya tiene una reserva activa en ese período."
            )

        reservation = Reservation(
            hotel_id=hotel_id,
            room_id=data.room_id,
            client_id=data.client_id,
            created_by=user_id,
            start_date=data.start_date,
            end_date=data.end_date,
            status="pending",
            advance_payment=data.advance_payment,
            notes=data.notes,
        )

        try:
            created = await self.reservation_repository.create(reservation)
            await self.db.commit()
            await self.db.refresh(created)
            return created
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(
                "No se pudo crear la reserva (datos inconsistentes o restricción en base de datos)."
            ) from None

    async def list_reservations(self, hotel_id: int) -> list[Reservation]:
        return await self.reservation_repository.list_by_hotel(hotel_id)

    async def get_reservation_by_id(
        self, hotel_id: int, reservation_id: int
    ) -> Reservation | None:
        return await self.reservation_repository.get_by_id_and_hotel(
            hotel_id, reservation_id
        )