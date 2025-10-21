from fastapi import HTTPException
from sqlmodel import Session, select
from controller.controller_generic import create_crud_router, Hooks
from model.models import Person, Address
from model.dto import PersonCreate, PersonUpdate, PersonRead


class PersonHooks(Hooks[Person, PersonCreate, PersonUpdate]):
    def pre_create(self, payload: PersonCreate, session: Session) -> None:
        if payload.address_id is not None and payload.address_id != 0:
            if not session.get(Address, payload.address_id):
                raise HTTPException(400, "Address do not exists")
    
    def pre_update(self, payload: PersonUpdate, session: Session, obj: Person) -> None:
        # se vai alterar team_id, valida
        if payload.address_id is not None:
            if payload.address_id != 0 and not session.get(Address, payload.address_id):
                raise HTTPException(400, "Address do not exists")

router = create_crud_router(
    model=Person,
    create_schema=PersonCreate,
    update_schema=PersonUpdate,
    read_schema=PersonRead,
    prefix="/persons",
    tags=["persons"],
    hooks=PersonHooks(),
)

"""
router = APIRouter(prefix="/persons", tags=["Persons"])

def get_person_service(session: SessionDep) -> PersonService:
    return PersonService(session)

ServiceDep = Annotated[PersonService, Depends(get_person_service)]

@router.post("/", response_model=PersonPublic, status_code=201)
def create_person(person: PersonCreate, service: ServiceDep):
    return service.create(person)


@router.get("/{person_id}", response_model=PersonPublic)
def read_person(person_id: int, service: ServiceDep):
    return service.get(person_id)

@router.patch("/{person_id}", response_model=PersonPublic)
def update_person(person_id: int, person: PersonUpdate, service: ServiceDep):
    return service.update(person_id, person)

@router.delete("/{person_id}", status_code=204)
def delete_hero(person_id: int, service: ServiceDep):
    service.delete(person_id)
    return None
"""