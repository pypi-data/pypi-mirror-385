from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated
from fastapi import Depends

### SQLModel Classes creating


# DATABASE CONFIG TO CONNECT TO CODE

# Creating the Engine of SQLModel --> this is what holds the connections to the database
# It's necessary just one engine object for the code to connect to the database.
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# {"check_same_thread": False} allows fastAPI to use the same SQLite db in different thread.
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

#creating the tables for all the table models (Pessoa class above)
#def create_db_and_tables():
    #SQLModel.metadata.create_all(engine)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)


# Creating a Session Dependency --> Session will store the object in memory and keep track of any changes needed in the data, 
# then it uses the engine to communicate with the database.
def get_session():
    with Session(engine) as session:
        yield session

# session dependency
SessionDep = Annotated[Session, Depends(get_session)]


# Creating Database Tables on the app inicialization
#@app.on_event("startup")
#def on_startup():
    # Calls the method that will create all the db tables from the SQLModels created above.
    #create_db_and_tables() 