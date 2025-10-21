from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
import uuid

from healthdatalayer.models import Client


if TYPE_CHECKING:
    from healthdatalayer.models import ClientLab
    

class Px(Client, table=True):
    __tablename__ = "px"
    
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    
    marriage_status_id: Optional[uuid.UUID] = Field(default=None, foreign_key="marriage_status.marriage_status_id")
    profession_id: Optional[uuid.UUID] = Field(default=None, foreign_key="profession.profession_id")
    education_id: Optional[uuid.UUID] = Field(default=None, foreign_key="education.education_id")
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.user_id")

Px.marriage_status = Relationship()
Px.profession = Relationship()
Px.education = Relationship()
Px.user = Relationship()
Px.medical_labs = Relationship(back_populates="pxs", link_model="ClientLab")