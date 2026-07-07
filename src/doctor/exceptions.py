
from src.exceptions import NotFoundException


class DoctorNotFoundException(NotFoundException):
    detail = "Доктор не найден"