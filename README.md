# CHESS PROJECT

## Phase I

### Configuration

#### Postgres & docker

```
docker run --name new-postgres-container --network pgnetwork -e POSTGRES_USER=chessgeeks -e POSTGRES_PASSWORD=soen363 -e POSTGRES_DB=chess_db -p 5433:5432 -d postgres

```

#### PSYCOPG2 - interaction with db

```
pip3 install psycopg2
```

### Steps to create the DB:

1. Ensure python and postgres and docker are installed (python --version & postgres --version & docker --version)
2. Start by running the above commands
3. Run db_instance.py
4. Run db_pop_pgn.py
