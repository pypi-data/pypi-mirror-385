from sqlmodel import Session, select
from typing import List, Optional
from model.dto import AddressCreate, AddressUpdate, AddressPublic
from model.models import Address


class AddressRepository:
    
    def __init__(self, session:Session):
        self.session = session
    
    # ADDRESS

    # Creating a Address
    #@app.post("/create_address/", response_model=AddressPublic)
    def create(self, address: AddressCreate) -> AddressPublic:
        db_address = Address.model_validate(address)
        self.session.add(db_address)
        self.session.commit()
        self.session.refresh(db_address)
        return db_address



    # Read a Address from database by id
    #@app.get("/read_address/{address_id}", response_model=AddressPublic)
    def read(self, address_id: int) -> Address:
        address = session.get(Address, address_id)
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        return address


    # Update a Address
    #@app.patch("/update_address/{address_id}", response_model=AddressPublic)
    def update(self, address_id:int, address:AddressUpdate):
        db_address = session.get(Address, address_id)
        if not db_address:
            raise HTTPException(status_code=404, detail="Hero not found")
        address_data = address.model_dump(exclude_unset=True)
        db_address.sqlmodel_update(address_data)
        self.session.add(db_address)
        self.session.commit()
        self.session.refresh(db_address)
        return db_address


    # Delete address from the database
    #@app.delete("/address_delete/{address_id}")
    def delete(self, address_id: int):
        address = session.get(Address, address_id)
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        self.session.delete(address)
        self.session.commit()
        return {"ok": True}