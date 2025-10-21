from fastapi import HTTPException, status
from typing import List
from sqlmodel import Session
from model.models import Person
from model.dto import PersonCreate, PersonUpdate, PersonPublic
from repository.person_repository import PersonRepository
from repository.address_repository import AddressRepository


class PersonService:

    def __init__(self, session:Session):
        self.repo = PersonRepository(session)
        self.address_repo = AddressRepository(session)
    
    def create(self, payload:PersonCreate) -> PersonPublic:
        person = self.repo.create(payload)
        return PersonPublic.model_validate(person)


    def get(self, person_id: int) -> PersonPublic:
        person = self.repo.get(person_id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
        return PersonPublic.model_validate(person)

    def update(self, person_id: int, payload: PersonUpdate) -> PersonPublic:
        person = self.repo.get(person_id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
        person = self.repo.update(person, payload)
        return PersonPublic.model_validate(person)

    def delete(self, person_id: int) -> None:
        person = self.repo.get(person_id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
        self.repo.delete(person)