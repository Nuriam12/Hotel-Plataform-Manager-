from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stay import Stay
from app.repositories.client_repository import ClientRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.stay_repository import StayRepository
from app.schemas.stay import StayCreate


class StayService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.stay_repository = StayRepository(db)
        self.room_repository = RoomRepository(db)
        self.client_repository = ClientRepository(db)
        self.reservation_repository = ReservationRepository(db)

    async def check_in(
        self,
        hotel_id: int,
        user_id: int,
        data: StayCreate,
    ) -> Stay:
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

        if data.reservation_id is not None:
            res = await self.reservation_repository.get_by_id_and_hotel(
                hotel_id, data.reservation_id
            )
            if res is None:
                raise LookupError("La reserva no existe en este hotel.")
            if res.status == "cancelled":
                raise ValueError(
                    "No se puede hacer check-in sobre una reserva cancelada."
                )
            if res.room_id != data.room_id or res.client_id != data.client_id:
                raise ValueError(
                    "La reserva no coincide con la habitación o el cliente indicados."
                )

        if await self.stay_repository.has_active_stay_for_room(
            hotel_id, data.room_id
        ):
            raise ValueError(
                "La habitación ya tiene una estancia activa (sin check-out)."
            )

        checkin = data.checkin_datetime
        if checkin is None:
            checkin = datetime.now(timezone.utc).replace(tzinfo=None)

        stay = Stay(
            hotel_id=hotel_id,
            room_id=data.room_id,
            client_id=data.client_id,
            reservation_id=data.reservation_id,
            created_by=user_id,
            checkin_datetime=checkin,
            checkout_datetime=None,
            price_per_night=data.price_per_night,
            status="active",
            notes=data.notes,
        )

        try:
            created = await self.stay_repository.create(stay)
            await self.db.commit()
            await self.db.refresh(created)
            return created
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(
                "No se pudo registrar la estancia (restricción en base de datos)."
            ) from None

    async def check_out(self, hotel_id: int, stay_id: int) -> Stay:
        stay = await self.stay_repository.get_by_id_and_hotel(hotel_id, stay_id)
        if stay is None:
            raise LookupError("La estancia no existe en este hotel.")
        if stay.checkout_datetime is not None:
            raise ValueError("Esta estancia ya tiene check-out registrado.")

        stay.checkout_datetime = datetime.now(timezone.utc).replace(tzinfo=None)
        stay.status = "completado"

        await self.db.commit()
        await self.db.refresh(stay)
        return stay

    async def list_stays(self, hotel_id: int) -> list[Stay]:
        return await self.stay_repository.list_by_hotel(hotel_id)

    async def get_stay_by_id(
        self, hotel_id: int, stay_id: int
    ) -> Stay | None:
        return await self.stay_repository.get_by_id_and_hotel(hotel_id, stay_id)