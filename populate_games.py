import time
from datetime import datetime
import chess.pgn
import mysql.connector
import requests



db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database='lichess'
)
cursor = db.cursor()

pgn = open("lichess_db_standard_rated_2013-01.pgn")

done = False
known_users = set()
known_tournaments = set()

while True:
    try:
        game = chess.pgn.read_game(pgn)

        event_id = game.headers.get('Site').split('/')[-1]
        cursor.execute(f"SELECT * FROM EVENT E WHERE E.id = '{event_id}'")
        if cursor.fetchall():
            continue

        event_string = game.headers.get('Event').split()

        event = ' '.join(event_string[0:3])
        tournamentId = event_string[4].split('/')[-1] if len(event_string) == 4 else None

        whiteId = game.headers.get('White')
        blackId = game.headers.get('Black')
        whiteElo = int(game.headers.get('WhiteElo'))
        blackElo = int(game.headers.get('BlackElo'))
        whiteRatingDiff = int(game.headers.get('WhiteRatingDiff'))
        blackRatingDiff = int(game.headers.get('BlackRatingDiff'))
        opening = game.headers.get('Opening')
        termination = game.headers.get('Termination')
        timeControl = game.headers.get('TimeControl')
        result = game.headers.get('Result')
        UTCDate = game.headers.get('UTCDate')
        UTCTime = game.headers.get('UTCTime')
        moves = game.mainline_moves()

        # fetch users
        for userId in (blackId, whiteId):

            if userId in known_users:
                continue

            known_users.add(userId)

            cursor.execute(f"SELECT * FROM USER E WHERE E.id = '{userId}'")
            if cursor.fetchall():
                continue

            print(f'attempting to fetch user {userId}')
            request = requests.get(f'https://lichess.org/api/user/{userId}')
            while request.status_code != 200:
                print(f'got a 427 for user {userId} at {datetime.now()}')
                time.sleep(600)
                request = requests.get(f'https://lichess.org/api/user/{userId}')

            user_json = request.json()

            id = user_json.get('id')
            createdAt = user_json.get('createdAt')
            seenAt = user_json.get('seenAt') if user_json.get('seenAt') else 'NULL'
            playtimeTotal = user_json.get('playTime').get('total')
            url = user_json.get('url')
            # insert user into database
            insert_statement = f"INSERT INTO USER(id, createdAt, seenAt, playtimeTotal, url)\n" \
                               f"VALUES\n" \
                               f"('{id}', {createdAt}, {seenAt}, {playtimeTotal}, '{url}')"
            print(f'attempting to insert user {id} into database')
            try:
                cursor.execute(insert_statement)
            except Exception as E:
                print(f'failed to insert user {id} into database')

        # fetch tournament
        if tournamentId and tournamentId not in known_tournaments:
            cursor.execute(f"SELECT * FROM TOURNAMENT T WHERE T.id = '{tournamentId}'")

            known_tournaments.add(tournamentId)

            if cursor.fetchall():
                continue

            print(f'attempting to fetch tournament {tournamentId}')
            request = requests.get(f'https://lichess.org/api/tournament/{tournamentId}')
            while request.status_code != 200:
                print(f'got a 427 for tournament {tournamentId} at {datetime.now()}')
                time.sleep(600)
                request = requests.get(f'https://lichess.org/api/tournament/{tournamentId}')
            user_json = request.json()

            id = user_json.get('id')
            startsAt = user_json.get('startsAt')
            system = user_json.get('system')
            fullName = user_json.get('fullName')
            key = user_json.get('key')
            clockLimit = user_json.get('clock', {}).get('limit')
            clockIncrement = user_json.get('clock').get('increment')
            minutes = user_json.get('minutes')
            variant = user_json.get('variant')
            nbPlayers = user_json.get('nbPlayers')
            rated = user_json.get('rated')
            headline = user_json.get('headline')
            berserkable = user_json.get('berserkable')
            description = user_json.get('description')

            # insert tournament into database
            insert_statement = f"INSERT INTO tournament(id, startsAt, system, fullName, key, clockLimit, clockIncrement, minutes, variant, nbPlayers, rated, headline, berserkable, description)" \
                               f"VALUES" \
                               f"('{id}', '{startsAt}', '{system}', '{fullName}', '{key}', {clockLimit}, {clockIncrement}, {minutes}, '{variant}', {nbPlayers}, {rated}, '{headline}', {berserkable}, '{description}')"
            print(f'attempting to insert tournament {tournamentId} into database')
            try:
                cursor.execute(insert_statement)
            except Exception as E:
                print(f'failed to insert tournament {tournamentId} into database')

        # insert event into database
        insert_statement = \
                    f"INSERT INTO EVENT(id, event, tournamentId, whiteId, blackId, UTCDate, UTCTime, " \
                    f"whiteElo, blackElo, whiteRatingDiff, blackRatingDiff, opening, timeControl," \
                    f" result, termination, moves)\n" \
                    f"VALUES\n" \
                    f"('{event_id}', '{event}', '{tournamentId}', '{whiteId}', '{blackId}', '{UTCDate}', '{UTCTime}'," \
                    f"{whiteElo}, {blackElo}, {whiteRatingDiff}, {blackRatingDiff}, \"{opening}\", {timeControl}," \
                    f"'{result}', '{termination}', '{moves}')" \
            if tournamentId else \
                    f"INSERT INTO EVENT(id, event, tournamentId, whiteId, blackId, UTCDate, UTCTime, " \
                    f"whiteElo, blackElo, whiteRatingDiff, blackRatingDiff, opening, timeControl," \
                    f" result, termination, moves)\n" \
                    f"VALUES\n" \
                    f"('{event_id}', '{event}', NULL, '{whiteId}', '{blackId}', '{UTCDate}', '{UTCTime}'," \
                    f"{whiteElo}, {blackElo}, {whiteRatingDiff}, {blackRatingDiff}, \"{opening}\", {timeControl}," \
                    f"'{result}', '{termination}', '{moves}')"

        print(f'attempting to insert event {event_id} into database')
        try:
            cursor.execute(insert_statement)
        except Exception:
            print(f'Failed to to insert event {event_id} into database ')
        db.commit()

    except Exception as E:
        continue

print('finished')
