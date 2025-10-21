from sqlmodel import Session, select
from typing import List, Optional
from model.dto import PersonCreate, PersonUpdate
from model.models import Person


class PersonRepository:
    def __init__(self, session:Session):
        self.session = session

    def get(self, person_id: int) -> Optional[Person]:
        return self.session.get(Person, person_id)

    # Creating a Person
    #@app.post("/create_person/", response_model=PersonPublic)
    def create(self, person: PersonCreate):
        db_person = Person.model_validate(person)
        self.session.add(db_person)
        self.session.commit()
        self.session.refresh(db_person)
        return db_person


    # Read Persons from the database
    #@app.get("/read_persons/", response_model=list[PersonPublic])
    #def read_persons(
    #    offset: int = 0,
    #    limit: Annotated[int, Query(le = 100)] = 100,
    #) -> list[Person]:
    #    persons = session.exec(select(Person).offset(offset).limit(limit)).all()
     #   return persons

    # Read a Person from database by id
    #@app.get("/read_person/{person_id}", response_model=PersonPublic)
    def read_person(self, person_id: int) -> Person:
        person = session.get(Person, person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person

    # Update a Person
    #@app.patch("/update_person/{person_id}", response_model=PersonPublic)
    def update(self, person_id:int, person: PersonUpdate):
        db_person = session.get(Person, person_id)
        if not db_person:
            raise HTTPException(status_code=404, detail="Person not found")
        person_data = person.model_dump(exclude_unset=True)
        db_person.sqlmodel_update(person_data)
        self.session.add(db_person)
        self.session.commit()
        self.session.refresh(db_person)
        return db_person


    # Delete Person from database by id
    #@app.delete("/person/{person_id}")
    def delete(self, person_id: int):
        person = session.get(Person, person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        self.session.delete(person)
        self.session.commit()
        return {"ok": True}