from typing import Optional, List
from uuid import UUID
from sqlmodel import select, or_
from sqlalchemy.orm import selectinload,joinedload
from healthdatalayer.models import Collaborator
from healthdatalayer.models import Speciality
from healthdatalayer.config.db import engines, get_session

class CollaboratorRepository:
    def __init__(self, tenant: str):
        self.tenant = tenant
        if tenant not in engines:
            raise ValueError(f"Tenant {tenant} is not configured")
        
    def create_command(self, collaborator: Collaborator) -> Collaborator:
        with get_session(self.tenant) as session:
            session.add(collaborator)
            session.commit()
            session.refresh(collaborator)
            return collaborator
        
    def get_by_id_command(self, collaborator_id: UUID, load_relations: bool = False) -> Optional[Collaborator]:
        with get_session(self.tenant) as session:
            if load_relations:
                statement = select(Collaborator).where(Collaborator.collaborator_id == collaborator_id).options(
                    selectinload(Collaborator.specialties)
                )
                collaborator = session.exec(statement).first()
                if load_relations:
                    
                    if collaborator.collaborator_type_id:
                        from healthdatalayer.models.collaborator.collaborator_type import CollaboratorType
                        collab_type_obj = session.get(CollaboratorType, collaborator.collaborator_type_id)
                        object.__setattr__(collaborator,'collaborator_type', collab_type_obj)
                        
                    if collaborator.user_id:
                        from healthdatalayer.models.user.user import User
                        user_obj = session.get(User, collaborator.user_id)
                        object.__setattr__(collaborator,'user',user_obj)
                        
                return collaborator
            else:
                return session.get(Collaborator, collaborator_id)
    
    def get_by_ruc_name_code_command(self, content: str, active_only: bool = True, load_relations : bool = False)->List[Collaborator]:
        with get_session(self.tenant) as session:
            
            query = select(Collaborator).where(
                    or_(
                        Collaborator.name.ilike(f"%{content}%"),
                        Collaborator.ruc.ilike(f"%{content}%"),
                        Collaborator.code.ilike(f"%{content}%")
                    )
                )
            
            if load_relations:
                query = select(Collaborator).options(
                    selectinload(Collaborator.collaborator_type),
                    joinedload(Collaborator.user),
                    selectinload(Collaborator.specialties)
                ).where(
                    or_(
                        Collaborator.name.ilike(f"%{content}%"),
                        Collaborator.ruc.ilike(f"%{content}%"),
                        Collaborator.code.ilike(f"%{content}%")
                    )
                )

            if active_only:
                query.where(Collaborator.is_active == True)
                
            collaborators = session.exec(query).all()
            
            return collaborators
                
            
    def get_all_command(self, active_only: bool = True,load_related: bool = False) -> List[Collaborator]:
        with get_session(self.tenant) as session:
            
            
            if load_related:
                
                statement = select(Collaborator).options(
                    selectinload(Collaborator.specialties)
                )
                if active_only:
                    statement = statement.where(Collaborator.is_active == True)
                collaborators = session.exec(statement).all()
                
                for collaborator in collaborators:
                    if collaborator.collaborator_type_id:
                        from healthdatalayer.models.collaborator.collaborator_type import CollaboratorType
                        collab_type_obj = session.get(CollaboratorType, collaborator.collaborator_type_id)
                        object.__setattr__(collaborator,'collaborator_type', collab_type_obj)
                        
                    if collaborator.user_id:
                        from healthdatalayer.models.user.user import User
                        user_obj = session.get(User, collaborator.user_id)
                        object.__setattr__(collaborator,'user',user_obj)
                return collaborators
            
            statement = select(Collaborator)
            return session.exec(statement).all()
    
    def update_command(self, collaborator: Collaborator) -> Collaborator:
        with get_session(self.tenant) as session:
            existing_collaborator = session.get(Collaborator, collaborator.collaborator_id)
            if not existing_collaborator:
                raise ValueError(f"collaborator with id {collaborator.collaborator_id} does not exist")
            
            for key, value in collaborator.dict(exclude_unset=True).items():
                setattr(existing_collaborator, key, value)
            
            bd_collaborator =  session.merge(existing_collaborator)
            session.commit()
            session.refresh(bd_collaborator)
            return bd_collaborator
        
    def delete_command(self, collaborator_id: UUID, soft_delete: bool = False)->None:
        with get_session(self.tenant) as session:
            existing_bridge = session.get(Collaborator, collaborator_id)
            if not existing_bridge:
                raise ValueError(f"Collaborator with id {collaborator_id} does not exist")

            if soft_delete:
                existing_bridge.is_active = False
                session.add(existing_bridge)
            else:
                session.delete(existing_bridge)

            session.commit()
    
    def assign_speciality_command(self, collaborator_id: UUID, speciality_id: UUID) -> Optional[Collaborator]:
        with get_session(self.tenant) as session:
            collab_statement = select(Collaborator).options(selectinload(Collaborator.specialties)).where(Collaborator.collaborator_id == collaborator_id)
            collab = session.exec(collab_statement).first()
            if not collab:
                return None
            
            speciality = session.get(Speciality, speciality_id)
            if not speciality:
                return None
            
            if speciality not in collab.specialties:
                collab.specialties.append(speciality)
                session.add(collab)
                session.commit()
                session.refresh(collab)
            
            return collab