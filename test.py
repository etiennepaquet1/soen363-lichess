import time

import mysql.connector
import lichess

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database='lichess'
)
cursor = db.cursor()

API_KEY = 'lip_cCtQVPpg50AfVhvHAiht'
client = lichess.Client(token=API_KEY)
members = client.get_team_members('lichess-swiss')


print('done')
