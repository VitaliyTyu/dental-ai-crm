from fastapi import APIRouter, status

from src.patient.dependencies import PatientServiceDep, ValidPatientDep
from src.patient.schemas import PatientCreate, PatientRead, PatientUpdate

patient_router = APIRouter(prefix="/patients", tags=["patients"])


@patient_router.post(
    "",
    response_model=PatientRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create patient",
)
async def create_patient(
    data: PatientCreate, patient_service: PatientServiceDep
):
    return await patient_service.create_patient(data)


@patient_router.get("", response_model=list[PatientRead], summary="Get patients")
async def get_patients(patient_service: PatientServiceDep):
    return await patient_service.get_patients()


@patient_router.get(
    "/{patient_id}", response_model=PatientRead, summary="Get patient by id"
)
async def get_patient(patient: ValidPatientDep):
    return patient


@patient_router.get(
    "/by-phone/{phone}",
    response_model=PatientRead,
    summary="Get patient by phone",
)
async def get_patient_by_phone(phone: str, patient_service: PatientServiceDep):
    return await patient_service.get_patient_by_phone(phone)


@patient_router.patch(
    "/{patient_id}", response_model=PatientRead, summary="Update patient data"
)
async def update_pateient(
    patient_id: int, data: PatientUpdate, patient_service: PatientServiceDep
):
    return await patient_service.update_patient(patient_id, data)


@patient_router.delete(
    "/{patient_id}",
    response_model=bool,
    summary="Delete patient by id"
)
async def delete_patient(patient_id: int, patient_service: PatientServiceDep):
    return await patient_service.delete_patient(patient_id)