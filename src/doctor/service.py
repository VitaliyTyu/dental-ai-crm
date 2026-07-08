from sqlalchemy.ext.asyncio import AsyncSession

from src.dental_service.exceptions import DentalServiceNotFoundException
from src.dental_service.models import DentalService
from src.dental_service.repository import DentalServiceRepository
from src.doctor.exceptions import DoctorNotFoundException
from src.doctor.models import Doctor, DoctorWorkingHour
from src.doctor.repository import DoctorRepository
from src.doctor.schemas import DoctorCreate, DoctorUpdate, DoctorWorkingHourInput


class DoctorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.doctor_repository = DoctorRepository(db)
        self.dental_service_repository = DentalServiceRepository(db)

    async def get_doctor_by_id(self, doctor_id: int) -> Doctor:
        doctor = await self.doctor_repository.get_by_id(doctor_id)
        if doctor is None:
            raise DoctorNotFoundException()
        return doctor

    async def get_doctors(self) -> list[Doctor]:
        return await self.doctor_repository.get_all()

    async def get_active_doctors(self) -> list[Doctor]:
        return await self.doctor_repository.get_active()

    async def create_doctor(self, data: DoctorCreate) -> Doctor:
        dental_services = await self._get_dental_services_or_none(
            data.dental_service_ids
        )

        working_hours = self._build_working_hours_or_none(data.working_hours)

        doctor = Doctor(
            name=data.name,
            specialization=data.specialization,
            dental_services=dental_services or [],
            working_hours=working_hours or [],
        )

        doctor = await self.doctor_repository.create(doctor)
        await self.db.commit()
        await self.db.refresh(doctor, attribute_names=["dental_services"])

        return doctor

    async def update_doctor(self, doctor_id: int, data: DoctorUpdate) -> Doctor:
        doctor = await self.doctor_repository.get_by_id(doctor_id)

        if doctor is None:
            raise DoctorNotFoundException()

        update_data = data.model_dump(
            exclude_unset=True, exclude={"dental_service_ids", "working_hours"}
        )

        dental_services = await self._get_dental_services_or_none(
            data.dental_service_ids
        )

        working_hours = self._build_working_hours_or_none(data.working_hours)

        doctor = await self.doctor_repository.update(
            doctor, update_data, dental_services, working_hours
        )
        await self.db.commit()

        return doctor

    async def delete_doctor(self, doctor_id) -> bool:
        doctor = await self.doctor_repository.get_by_id(doctor_id)
        if doctor is None:
            raise DoctorNotFoundException()
        await self.doctor_repository.delete(doctor)
        await self.db.commit()
        return True

    async def _get_dental_services_or_none(
        self, dental_service_ids: list[int] | None
    ) -> list[DentalService] | None:

        if dental_service_ids is None:
            return None

        dental_services = await self.dental_service_repository.get_by_ids(
            dental_service_ids
        )

        if len(dental_services) != len(set(dental_service_ids)):
            raise DentalServiceNotFoundException()

        return dental_services

    def _build_working_hours_or_none(
        self, working_hours: list[DoctorWorkingHourInput] | None
    ) -> list[DoctorWorkingHour] | None:
        if working_hours is None:
            return None

        return [
            DoctorWorkingHour(**working_hour.model_dump())
            for working_hour in working_hours
        ]
