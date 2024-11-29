Contibutors:

Etienne Paquet - 40208596
Kaoutar El Azzab - 40236580
Jordan Yeh - 40283075
Othmane Sbi - 40249134 


# CHESS PROJECT

## Phase I

### Configuration

#### Postgres & docker

```
docker run --name new-postgres-container --network pgnetwork -e POSTGRES_USER=chessgeeks -e POSTGRES_PASSWORD=soen363 -e POSTGRES_DB=chess_db -p 5433:5432 -d postgres
```

if you get the "pgnerwork not found":

```
docker run --name new-postgres-container -e POSTGRES_USER=chessgeeks -e POSTGRES_PASSWORD=soen363 -e POSTGRES_DB=chess_db -p 5433:5432 -d postgres
```

#### PSYCOPG2 - interaction with db

```
pip3 install psycopg2
```

#### Convert datetime in python to meet the API's data type

```
pip install python-dateutil
```

#### Install .env : important for the API key to work

```
pip install python-dotenv
```

#### Install requirements.txt

```
pip install requirements.txt
```

### Steps to create the DB:

1. Ensure python and postgres and docker are installed (python --version & postgres --version & docker --version)
2. Start by running the above commands
3. Run db_instance.py
4. Run db_pop_pgn.py

#### Request doesn't work unless a virtual environment is set (MAC USER ONLY)

```
python3 -m venv path/to/venv
```

```
python3 -m venv myenv
```

#### Activate the Virtual Environment :

```
source myenv/bin/activate
```

### Files of the project

- /DDL.sql : database instance script
- /full_access_views.sql : views script with full access
- /restricted_access_views.sql : views script with restricted access
- /complex_function_trigger.sql : the trigger function
- /db_instance.py : the python code to create the database instance in the database
- /db_pop_pgn.py : the data population
- /Queries.sql : the queries implementation
- /lichess_db_standard_rated_2013-01.pgn : metadata file with a load of data history
- /backups_csv : An example of an instance of our database.

## Phase II

The NoSQL database used : MongoDB (stores data in a flexible document-oriented format)

We're using the online plateform : MongoDB Atlas

All the libraries and dependencies used in 'phase i' are maintained (dotenv, psycopg2 and postgres)

### Python Libraries for this phase

#### Mongo for Python

```
pip install pymongo pymysql
```

```
pip install pymongo psycopg2
```

### Notes about the NoSql design

#### Changes Made During Migration to MongoDB

1. ISA Relationships

- In the relational model, playerType (player table) and event_type (event table) were implemented as ENUMs or foreign key relationships, distinguishing between different roles or types. In MongoDB, these are treated as simple fields (playerType in players and event_type in events), without the need for separate collections or inheritance-like structures. This change simplifies the schema while maintaining clarity in data representation.

2. Weak Entities

- Games: The game entity, which was dependent on the event entity, is embedded as an array of documents inside each event document in MongoDB. This change removes the need for a foreign key relationship between game and event, and instead allows each event document to contain all related game data directly.
- Gamemoves: The gamemoves entity, which was fully dependent on the game entity, is similarly embedded as an array of documents inside each game document. This allows all gamemoves related to a specific game to be stored directly within that game’s document, preserving the dependency while eliminating the need for a separate table and foreign key.

> Please read project_structure.txt for more info
