import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from healthdatalayer.models.medical_visit.medical_drug_recipe import MedicalDrugRecipe

if TYPE_CHECKING:
    from healthdatalayer.models.medical_visit.medical_recipe_visit import MedicalRecipeVisit

class MedicalDrug(SQLModel, table=True):
    __tablename__ = "medical_drug"

    medical_drug_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)

    drug_name:str
    stock:int
    drug_code:str
    supply_date: Optional[datetime] = Field(default=None)
    public_price:float

    is_active: bool = Field(default=True)

    medical_recipe_visits: List["MedicalRecipeVisit"] = Relationship(
        back_populates="medical_drugs",
        link_model=MedicalDrugRecipe
    )