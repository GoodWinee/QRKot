from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectUpdate)


class CRUDCharityProject(CRUDBase[
    CharityProject,
    CharityProjectCreate,
    CharityProjectUpdate
]):
    """Класс для управления проектами."""


charity_project = CRUDCharityProject(CharityProject)
