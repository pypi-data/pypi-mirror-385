import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class MedicalDrugRecipe(SQLModel, table=True):
    __tablename__ = "medical_drug_recipe"

    medical_drug_recipe_id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)

    medical_drug_id: uuid.UUID = Field(foreign_key="medical_drug.medical_drug_id", primary_key=True)
    medical_recipe_visit_id: uuid.UUID = Field(foreign_key="medical_recipe_visit.medical_recipe_visit_id", primary_key=True)
    
    quantity:int
    suplied:bool
    suplied_date: Optional[datetime] = Field(default=None)
    
    is_active: bool = Field(default=True)