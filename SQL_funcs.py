import config
import psycopg2
from psycopg2.extras import DictCursor

def SQL_Select(query, args):
    rows = ()
    conn = psycopg2.connect(dbname = config.DB_NAME, user = config.DB_USER, 
                        password = config.DB_PASSWORD, host = config.DB_HOST)
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        cursor.execute(query, args)
        rows = cursor.fetchall()
    except Exception as e:
        print (e)
    cursor.close()
    conn.close()
    return rows


def SQL_Update(query, args):
    conn = psycopg2.connect(dbname = config.DB_NAME, user = config.DB_USER, 
                        password = config.DB_PASSWORD, host = config.DB_HOST)
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        cursor.execute(query, args)
        conn.commit()
    except Exception as e:
        print (e)
        conn.rollback()
    cursor.close()
    conn.close()



def get_user(user_id):
    row = SQL_Select('select * from "secretary"."TS_USERS" u where u."TEAMS_ID" = %s', (user_id,))
    if len(row) == 0:
        return row
    else:
        return row[0]
    
def get_not_senders_by_hour(time):
    print(time)
    return SQL_Select(f'SELECT *' 
                      f'FROM secretary."TS_USERS" u '
                      f'where u."UTC_DIFF" = %s '
                      f'and u."TEAMS_ID" not in (select "TEAMS_ID" from secretary."TS_SENDERS" s)', (time,))
    #return ['adyevdv@sovcombank.ru']


def add_user(name, chat_id, diff, city):
   
    SQL_Update('INSERT INTO "secretary"."TS_USERS" ("TEAMS_ID", "NAME", "UTC_DIFF", "CITY") VALUES (%s, %s, %s, %s);',
                (chat_id, name, diff, city))
    

def set_silence(user_id, value):
    SQL_Update('UPDATE secretary."TS_USERS" SET "SILENCED" = %s WHERE "TEAMS_ID" = %s;', (value, user_id))

def shift_time_diff (user_id, new_time_diff):
    SQL_Update('UPDATE secretary."TS_USERS" SET "UTC_DIFF" = %s WHERE "TEAMS_ID" = %s;', (new_time_diff, user_id))

def add_sender (user_id):
    SQL_Update('INSERT INTO "secretary"."TS_SENDERS" ("TEAMS_ID") VALUES (%s);', (user_id,))
