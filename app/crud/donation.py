from app.crud.base import CRUDBase
from app.models.donation import Donation
from app.schemas.donation import DonationCreate


class CRUDDonation(CRUDBase[Donation, DonationCreate, None]):
    """Класс для управления пожертвованиями."""


donation = CRUDDonation(Donation)
