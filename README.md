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
