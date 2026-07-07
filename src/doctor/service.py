from sqlalchemy.ext.asyncio import AsyncSession

from src.dental_service.exceptions import DentalServiceNotFoundException
from src.dental_service.repository import DentalServiceRepository
from src.doctor.exceptions import DoctorNotFoundException
from src.doctor.models import Doctor
from src.doctor.repository import DoctorRepository
from src.doctor.schemas import DoctorCreate, DoctorUpdate


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
        dental_services = await self.dental_service_repository.get_by_ids(
            data.dental_service_ids
        )

        if len(dental_services) != len(set(data.dental_service_ids)):
            raise DentalServiceNotFoundException()

        doctor = Doctor(
            name=data.name,
            specialization=data.specialization,
            dental_services=dental_services,
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
            exclude_unset=True, exclude={"dental_service_ids"}
        )

        dental_services = None

        if data.dental_service_ids is not None:
            dental_services = await self.dental_service_repository.get_by_ids(
                data.dental_service_ids
            )

            if len(dental_services) != len(set(data.dental_service_ids)):
                raise DentalServiceNotFoundException()

        doctor = await self.doctor_repository.update(
            doctor, update_data, dental_services
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
