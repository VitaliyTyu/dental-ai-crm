
from src.exceptions import NotFoundException


class AppointmentNotFoundException(NotFoundException):
    detail = "Встреча не найдена"