from controller.controller_generic import create_crud_router
from model.models import Address 
from model.dto import AddressCreate, AddressUpdate, AddressRead

router = create_crud_router(
    model=Address,
    create_schema=AddressCreate,
    update_schema=AddressUpdate,
    read_schema=AddressRead,
    prefix="/address",
    tags=["address"],
)