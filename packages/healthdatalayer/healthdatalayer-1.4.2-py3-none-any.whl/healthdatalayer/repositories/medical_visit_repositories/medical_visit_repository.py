from typing import Optional, List
from uuid import UUID
from sqlmodel import select, or_
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import MedicalVisit
from healthdatalayer.config.db import engines, get_session

class MedicalVisitRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
    
    def create_command(self, medical_visit: MedicalVisit) -> MedicalVisit:
        with get_session(self.tenant) as session:
            session.add(medical_visit)
            session.commit()
            session.refresh(medical_visit)
            return medical_visit
    
    def get_by_id_command(self, medical_visit_id: UUID, load_relations: bool = False) -> Optional[MedicalVisit]:
        with get_session(self.tenant) as session:
            
            if load_relations:
                statement = select(MedicalVisit).where(MedicalVisit.medical_visit_id == medical_visit_id).options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
                medical_visit = session.exec(statement).first()
               
                return medical_visit
            else:
                return session.get(MedicalVisit, medical_visit_id)
    
    def list_all_command(self, active_only: bool = True, load_relations: bool = False)->List[MedicalVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalVisit)
            
            if load_relations:
                
                statement = select(MedicalVisit).options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
                if active_only:
                    statement = statement.where(MedicalVisit.is_active == True)
                medical_visits = session.exec(statement).all()
              
                return medical_visits
            
            statement = select(MedicalVisit)
            return session.exec(statement).all()
    
    def get_by_client_id_command(self, client_id: UUID, active_only: bool = True, load_relations: bool = False) -> List[MedicalVisit]:
        with get_session(self.tenant) as session:
            statement = select(MedicalVisit).where(MedicalVisit.client_id == client_id)
            if active_only:
                statement = statement.where(MedicalVisit.is_active == True)
            if load_relations:
                statement = statement.options(
                    joinedload(MedicalVisit.client),
                    joinedload(MedicalVisit.collaborator),
                    joinedload(MedicalVisit.speciality),
                    selectinload(MedicalVisit.medical_diagnosis_visits),
                    selectinload(MedicalVisit.medical_recipe_visits),
                    selectinload(MedicalVisit.organ_system_reviews),
                    selectinload(MedicalVisit.physical_exams)
                )
            
            medical_visits = session.exec(statement).all()
            return medical_visits
    
    def update_command(self, medical_visit: MedicalVisit) -> MedicalVisit:
        with get_session(self.tenant) as session:
            existing_medical_visit = session.get(MedicalVisit, medical_visit.medical_visit_id)
            if not existing_medical_visit:
                raise ValueError(f"medical_visit with id {medical_visit.medical_visit_id} does not exist")
            
            for key, value in medical_visit.dict(exclude_unset=True).items():
                setattr(existing_medical_visit, key, value)
            
            bd_medical_visit =  session.merge(existing_medical_visit)
            session.commit()
            session.refresh(bd_medical_visit)
            return bd_medical_visit
        
    def delete_command(self, medical_visit_id: UUID, soft_delete: bool = False)->None:
        with get_session(self.tenant) as session:
            existing_bridge = session.get(MedicalVisit, medical_visit_id)
            if not existing_bridge:
                raise ValueError(f"MedicalVisit with id {medical_visit_id} does not exist")

            if soft_delete:
                existing_bridge.is_active = False
                session.add(existing_bridge)
            else:
                session.delete(existing_bridge)

            session.commit()
    