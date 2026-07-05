
from sqlalchemy.ext.asyncio import AsyncSession

from src.doctor.models import Doctor
from src.doctor.repository import DoctorRepository
from src.doctor.schemas import DoctorCreate, DoctorUpdate
from src.exceptions import NotFoundException


class DoctorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.doctor_repository = DoctorRepository(db)
        
    async def get_doctor_by_id(self, doctor_id: int) -> Doctor:
        doctor = await self.doctor_repository.get_by_id(doctor_id)
        if doctor is None:
            raise NotFoundException("Доктор не найден")
        return doctor
    
    async def get_doctors(self) -> list[Doctor]:
        return await self.doctor_repository.get_all()
    
    async def get_active_doctors(self) -> list[Doctor]:
        return await self.doctor_repository.get_active()
    
    async def create_doctor(self, data: DoctorCreate) -> Doctor:
        doctor = Doctor(name=data.name, specialization=data.specialization)
        doctor = await self.doctor_repository.create(doctor)
        await self.db.commit()
        return doctor
    
    async def update_doctor(self, doctor_id: int, data: DoctorUpdate) -> Doctor:
        doctor = await self.get_doctor_by_id(doctor_id)
        update_data = data.model_dump(exclude_unset=True)
        doctor = await self.doctor_repository.update(doctor, update_data)
        await self.db.commit()
        return doctor
    
    async def delete_doctor(self, doctor_id) -> bool:
        doctor = await self.get_doctor_by_id(doctor_id)
        await self.doctor_repository.delete(doctor)
        await self.db.commit()
        return True