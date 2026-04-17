from datetime import datetime, timezone
from decimal import Decimal
from math import ceil

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stay import Stay
from app.repositories.client_repository import ClientRepository
from app.repositories.consumption_repository import ConsumptionRepository
from app.repositories.inventory_product_repository import InventoryProductRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.stay_repository import StayRepository
from app.schemas.stay import AdditionalChargeUpdate, HotelSummaryResponse, StayAccountResponse, StayCreate


class StayService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.stay_repository = StayRepository(db)
        self.room_repository = RoomRepository(db)
        self.client_repository = ClientRepository(db)
        self.reservation_repository = ReservationRepository(db)
        self.consumption_repository = ConsumptionRepository(db)
        self.product_repository = InventoryProductRepository(db)

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _assert_stay_active(stay: Stay) -> None:
        """Lanza ValueError si la estancia ya está cerrada (completed)."""
        if stay.status == "completed":
            raise ValueError(
                "Esta cuenta corriente está cerrada. "
                "No se pueden realizar modificaciones tras el check-out."
            )

    @staticmethod
    def _calculate_nights(checkin: datetime, checkout: datetime | None) -> int:
        """
        Calcula noches ocupadas.
        Regla: noche empezada = noche cobrada. Mínimo 1.
        Si no hay checkout, calcula hasta ahora (cuenta corriente activa).
        """
        reference = checkout if checkout else datetime.now(timezone.utc).replace(tzinfo=None)
        delta_seconds = (reference - checkin).total_seconds()
        return max(1, ceil(delta_seconds / 86400))

    # ------------------------------------------------------------------ #
    # Check-in                                                             #
    # ------------------------------------------------------------------ #

    async def check_in(
        self,
        hotel_id: int,
        user_id: int,
        data: StayCreate,
    ) -> Stay:
        room = await self.room_repository.get_by_id_and_hotel(hotel_id, data.room_id)
        if room is None:
            raise LookupError("La habitación no existe en este hotel.")

        client = await self.client_repository.get_by_id_and_hotel(hotel_id, data.client_id)
        if client is None:
            raise LookupError("El cliente no existe en este hotel.")

        if data.reservation_id is not None:
            res = await self.reservation_repository.get_by_id_and_hotel(
                hotel_id, data.reservation_id
            )
            if res is None:
                raise LookupError("La reserva no existe en este hotel.")
            if res.status == "cancelled":
                raise ValueError("No se puede hacer check-in sobre una reserva cancelada.")
            if res.room_id != data.room_id or res.client_id != data.client_id:
                raise ValueError(
                    "La reserva no coincide con la habitación o el cliente indicados."
                )

        if room.status == "occupied":
            raise ValueError("La habitación ya está ocupada.")

        if await self.stay_repository.has_active_stay_for_room(hotel_id, data.room_id):
            raise ValueError("La habitación ya tiene una estancia activa (sin check-out).")

        checkin = data.checkin_datetime
        if checkin is None:
            checkin = datetime.now(timezone.utc).replace(tzinfo=None)

        account_number = await self.stay_repository.next_account_number(hotel_id)

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
            account_number=account_number,
        )

        try:
            created = await self.stay_repository.create(stay)
            room.status = "occupied"
            await self.db.commit()
            await self.db.refresh(created)
            return created
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(
                "No se pudo registrar la estancia (restricción en base de datos)."
            ) from None

    # ------------------------------------------------------------------ #
    # Check-out                                                            #
    # ------------------------------------------------------------------ #

    async def check_out(self, hotel_id: int, stay_id: int) -> Stay:
        stay = await self.stay_repository.get_by_id_and_hotel(hotel_id, stay_id)
        if stay is None:
            raise LookupError("La estancia no existe en este hotel.")
        if stay.checkout_datetime is not None:
            raise ValueError("Esta estancia ya tiene check-out registrado.")

        room = await self.room_repository.get_by_id_and_hotel(hotel_id, stay.room_id)
        if room is None:
            raise LookupError("La habitación asociada no existe.")

        stay.checkout_datetime = datetime.now(timezone.utc).replace(tzinfo=None)
        stay.status = "completed"
        room.status = "available"

        await self.db.commit()
        await self.db.refresh(stay)
        return stay

    # ------------------------------------------------------------------ #
    # Cargo adicional (ADIC)                                               #
    # ------------------------------------------------------------------ #

    async def update_additional_charge(
        self,
        hotel_id: int,
        stay_id: int,
        data: AdditionalChargeUpdate,
    ) -> Stay:
        stay = await self.stay_repository.get_by_id_and_hotel(hotel_id, stay_id)
        if stay is None:
            raise LookupError("La estancia no existe en este hotel.")

        self._assert_stay_active(stay)

        stay.additional_charge = data.additional_charge
        stay.additional_charge_notes = data.additional_charge_notes

        await self.db.commit()
        await self.db.refresh(stay)
        return stay

    # ------------------------------------------------------------------ #
    # Cuenta corriente                                                     #
    # ------------------------------------------------------------------ #

    async def get_account(self, hotel_id: int, stay_id: int) -> StayAccountResponse:
        stay = await self.stay_repository.get_by_id_and_hotel(hotel_id, stay_id)
        if stay is None:
            raise LookupError("La estancia no existe en este hotel.")

        room = await self.room_repository.get_by_id_and_hotel(hotel_id, stay.room_id)
        if room is None:
            raise LookupError("La habitación asociada no existe.")

        client = await self.client_repository.get_by_id_and_hotel(hotel_id, stay.client_id)
        if client is None:
            raise LookupError("El cliente asociado no existe.")

        consumptions = await self.consumption_repository.list_by_stay(hotel_id, stay_id)

        consumption_lines = []
        for c in consumptions:
            product = await self.product_repository.get_by_id_and_hotel(
                hotel_id, c.product_id
            )
            product_name = product.name if product else f"Producto #{c.product_id}"
            subtotal = Decimal(str(c.unit_price)) * c.quantity
            consumption_lines.append(
                {
                    "id": c.id,
                    "product_id": c.product_id,
                    "product_name": product_name,
                    "quantity": c.quantity,
                    "unit_price": Decimal(str(c.unit_price)),
                    "subtotal": subtotal,
                    "created_at": c.created_at,
                    "is_cancelled": c.is_cancelled,
                }
            )

        nights = self._calculate_nights(stay.checkin_datetime, stay.checkout_datetime)
        nights_cost = Decimal(str(stay.price_per_night)) * nights
        consumptions_total = sum(
            line["subtotal"] for line in consumption_lines
            if not line["is_cancelled"]
        )
        additional = Decimal(str(stay.additional_charge)) if stay.additional_charge else Decimal("0")
        grand_total = nights_cost + consumptions_total + additional

        return StayAccountResponse(
            account_number=stay.account_number,
            stay={
                "id": stay.id,
                "status": stay.status,
                "checkin_datetime": stay.checkin_datetime,
                "checkout_datetime": stay.checkout_datetime,
                "price_per_night": Decimal(str(stay.price_per_night)),
                "notes": stay.notes,
                "additional_charge": additional if stay.additional_charge else None,
                "additional_charge_notes": stay.additional_charge_notes,
            },
            room={
                "id": room.id,
                "room_number": room.room_number,
                "room_type": room.room_type,
                "floor": room.floor,
            },
            client={
                "id": client.id,
                "name": client.name,
                "dni": client.dni,
                "phone": client.phone,
            },
            consumptions=consumption_lines,
            totals={
                "nights": nights,
                "nights_cost": nights_cost,
                "consumptions_total": consumptions_total,
                "additional_charge": additional,
                "grand_total": grand_total,
            },
        )

    # ------------------------------------------------------------------ #
    # Tablero de habitaciones                                              #
    # ------------------------------------------------------------------ #

    async def get_board(self, hotel_id: int) -> list[dict]:
        rows = await self.room_repository.get_board(hotel_id)
        board = []
        for room, stay, client in rows:
            entry: dict = {
                "id": room.id,
                "room_number": room.room_number,
                "floor": room.floor,
                "room_type": room.room_type,
                "price_per_night": Decimal(str(room.price_per_night)),
                "status": room.status,
                "active_stay": None,
            }
            if stay is not None and client is not None:
                nights = self._calculate_nights(stay.checkin_datetime, None)
                nights_cost = Decimal(str(stay.price_per_night)) * nights
                entry["active_stay"] = {
                    "stay_id": stay.id,
                    "account_number": stay.account_number,
                    "client_name": client.name,
                    "client_dni": client.dni,
                    "checkin_datetime": stay.checkin_datetime,
                    "nights_so_far": nights,
                    "total_estimate": nights_cost,
                }
            board.append(entry)
        return board

    # ------------------------------------------------------------------ #
    # Listados                                                             #
    # ------------------------------------------------------------------ #

    async def list_stays(
        self, hotel_id: int, status: str | None = None
    ) -> list[Stay]:
        return await self.stay_repository.list_by_hotel_filtered(hotel_id, status)

    async def get_stay_by_id(self, hotel_id: int, stay_id: int) -> Stay | None:
        return await self.stay_repository.get_by_id_and_hotel(hotel_id, stay_id)

    async def get_summary(self, hotel_id: int) -> HotelSummaryResponse:
        rooms = await self.room_repository.list_by_hotel(hotel_id)
        rooms_total = len(rooms)
        rooms_available = sum(1 for r in rooms if r.status == "available")
        rooms_occupied = rooms_total - rooms_available

        active_stays = await self.stay_repository.list_by_hotel_filtered(hotel_id, status="active")
        stays_active = len(active_stays)

        completed_this_month = await self.stay_repository.list_completed_this_month(hotel_id)
        stays_completed_this_month = len(completed_this_month)

        revenue = Decimal("0")
        for stay in completed_this_month:
            nights = self._calculate_nights(stay.checkin_datetime, stay.checkout_datetime)
            revenue += Decimal(str(stay.price_per_night)) * nights
            if stay.additional_charge:
                revenue += Decimal(str(stay.additional_charge))

        return HotelSummaryResponse(
            rooms_total=rooms_total,
            rooms_available=rooms_available,
            rooms_occupied=rooms_occupied,
            stays_active=stays_active,
            stays_completed_this_month=stays_completed_this_month,
            revenue_this_month=revenue,
        )
