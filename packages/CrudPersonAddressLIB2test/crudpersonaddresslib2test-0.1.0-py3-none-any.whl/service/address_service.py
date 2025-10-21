from fastapi import HTTPException, status
from typing import List
from sqlmodel import Session
from model.dto import AddressCreate, AddressUpdate, AddressPublic
from repository.address_repository import AddressRepository


class AddressService:

    def __init__(self, session: Session):
        self.repo = AddressRepository(session)

    def create(self, payload:AddressCreate) -> AddressPublic:
        address = self.repo.create(payload)
        return AddressPublic.model_validate(address)


    def get(self, address_id: int) -> AddressPublic:
        address = self.repo.get(address_id)
        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        return AddressPublic.model_validate(address)

    def update(self, address_id: int, payload: AddressUpdate) -> AddressPublic:
        address = self.repo.get(address_id)
        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        address = self.repo.update(address, payload)
        return AddressPublic.model_validate(address)

    def delete(self, address_id: int) -> None:
        address = self.repo.get(address_id)
        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        self.repo.delete(address)