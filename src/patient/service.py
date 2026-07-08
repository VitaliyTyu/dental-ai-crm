from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import ConflictException, NotFoundException
from src.patient.exceptions import PatientNotFoundException
from src.patient.models import Patient
from src.patient.repository import PatientRepository
from src.patient.schemas import PatientCreate, PatientUpdate


class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.patient_repository = PatientRepository(db)

    async def create_patient(self, data: PatientCreate) -> Patient:
        existing = await self.patient_repository.get_by_phone(data.phone)
        if existing is not None:
            raise ConflictException(
                "Пациент с таким номером телефона уже существует"
            )
        patient = Patient(phone=data.phone, name=data.name, notes=data.notes)
        patient = await self.patient_repository.create(patient)
        await self.db.commit()
        return patient

    async def get_patients(self) -> list[Patient]:
        return await self.patient_repository.get_all()

    async def get_patient_by_id(self, patient_id: int) -> Patient:
        patient = await self.patient_repository.get_by_id(patient_id)
        if patient is None:
            raise PatientNotFoundException()
        return patient

    async def get_patient_by_phone(self, phone: str) -> Patient:
        patient = await self.patient_repository.get_by_phone(phone)
        if patient is None:
            raise PatientNotFoundException()
        return patient

    async def update_patient(
        self, patient_id: int, data: PatientUpdate
    ) -> Patient:
        patient = await self.get_patient_by_id(patient_id)
        update_data = data.model_dump(exclude_unset=True)
        patient = await self.patient_repository.update(patient, update_data)
        await self.db.commit()
        return patient

    async def delete_patient(self, patient_id: int) -> bool:
        patient = await self.get_patient_by_id(patient_id)
        await self.patient_repository.delete(patient)
        await self.db.commit()
        return True
