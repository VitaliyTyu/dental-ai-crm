
from src.exceptions import NotFoundException


class PatientNotFoundException(NotFoundException):
    detail = "Пациент не найден"