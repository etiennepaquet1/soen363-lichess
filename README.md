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


Please read project_structure.txt for more info