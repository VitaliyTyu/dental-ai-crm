
from src.exceptions import NotFoundException


class DentalServiceNotFoundException(NotFoundException):
    detail = "Услуга не найдена"