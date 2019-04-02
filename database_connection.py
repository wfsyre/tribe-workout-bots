import os
import urllib.parse
import urllib.request
import psycopg2

from psycopg2 import sql
from slack_api import *

from flask import Flask, request, jsonify, make_response

app = Flask(__name__)


def add_num_posts(mention_id, event_time, name):
    # "UPDATE tribe_data SET num_posts=num_posts+1, WHERE name = 'William Syre' AND last_time != "
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "UPDATE tribe_data SET num_posts=num_posts+1 WHERE slack_id = %s"),
            [mention_id[0]])
        if cursor.rowcount == 0:
            cursor.execute(sql.SQL("INSERT INTO tribe_data VALUES (%s, 0, 0, 0, now(), -1, 1, %s, %s)"),
                           [name, mention_id[0], event_time])
            send_debug_message("%s is new to Tribe" % name)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)
        return True


def collect_stats(datafield, rev):
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "SELECT * FROM tribe_data WHERE workout_score > -1.0"), )
        leaderboard = cursor.fetchall()
        leaderboard.sort(key=lambda s: s[datafield], reverse=rev)  # sort the leaderboard by score descending
        string1 = "Leaderboard:\n"
        for x in range(0, len(leaderboard)):
            string1 += '%d) %s with %.1f points \n' % (x + 1, leaderboard[x][0], leaderboard[x][datafield])
        cursor.close()
        conn.close()
        return string1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)


def get_group_info():
    url = "https://slack.com/api/users.list?token=" + os.getenv('BOT_OATH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json


def get_emojis():
    url = 'https://slack.com/api/emoji.list?token=' + os.getenv('OATH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json


def add_to_db(names, addition, num_workouts, ids):  # add "addition" to each of the "names" in the db
    cursor = None
    conn = None
    num_committed = 0
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        for x in range(0, len(names)):
            print("starting", names[x])
            cursor.execute(sql.SQL(
                "SELECT workout_score FROM tribe_data WHERE slack_id = %s"), [str(ids[x])])
            score = cursor.fetchall()[0][0]
            score = int(score)
            if score != -1:
                cursor.execute(sql.SQL(
                    "UPDATE tribe_data SET num_workouts=num_workouts+%s, workout_score=workout_score+%s, last_post="
                    "now() WHERE slack_id = %s"),
                    [str(num_workouts), str(addition), ids[x]])
                conn.commit()
                send_debug_message("committed %s with %s points" % (names[x], str(addition)))
                print("committed %s" % names[x])
                num_committed += 1
            else:
                send_debug_message("invalid workout poster found " + names[x])
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return num_committed


def subtract_from_db(names, subtraction, ids):  # subtract "subtraction" from each of the "names" in the db
    cursor = None
    conn = None
    num_committed = 0
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        for x in range(0, len(names)):
            cursor.execute(sql.SQL(
                "UPDATE tribe_data SET workout_score = workout_score - %s WHERE slack_id = %s"),
                [subtraction, ids[x]])
            conn.commit()
            send_debug_message("subtracted %s" % names[x])
            num_committed += 1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return num_committed


def reset_scores():  # reset the scores of everyone
    cursor = None
    conn = None
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "UPDATE tribe_data SET num_workouts = 0, workout_score = 0, last_post = now() WHERE workout_score != -1"
        ))
        cursor.execute(sql.SQL(
            "DELETE FROM tribe_workouts"
        ))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()


def reset_talkative():  # reset the num_posts of everyone
    cursor = None
    conn = None
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "UPDATE tribe_data SET num_posts = 0 WHERE workout_score != -1"))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()


def add_reaction_info_date(date, yes, drills, injured, no):
    # "UPDATE tribe_data SET num_posts=num_posts+1, WHERE name = 'William Syre' AND last_time != "
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("SELECT * FROM reaction_info WHERE date = %s"), [date])
        if cursor.rowcount == 0:
            cursor.execute(
                sql.SQL("INSERT INTO reaction_info (date, yes, no, drills, injured) VALUES (%s, %s, %s, %s, %s)"),
                [date.strftime("%Y-%B-%d"), yes, no, drills, injured])
            conn.commit()
            cursor.close()
            conn.close()
            return True
        else:
            conn.commit()
            cursor.close()
            conn.close()
            send_debug_message("Found a repeat calendar post")
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)


def add_reaction_info_ts(ts):
    # "UPDATE tribe_data SET num_posts=num_posts+1, WHERE name = 'William Syre' AND last_time != "
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("UPDATE reaction_info SET timestamp = %s WHERE timestamp IS NULL"),
                       [ts])
        if cursor.rowcount == 1:
            conn.commit()
            cursor.close()
            conn.close()
            return True
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)

def check_reaction_timestamp(ts):
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("SELECT * FROM reaction_info WHERE timestamp = %s"), [ts])
        if cursor.rowcount == 1:
            stuff = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            print(stuff)
            return stuff
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return []
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)
        return []


def count_practice(id, date, number):
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL("UPDATE tribe_attendance SET \"" + date + "\" =%s where slack_id = %s"), [number, id])
        if cursor.rowcount == 1:
            conn.commit()
            cursor.close()
            conn.close()
            send_debug_message("marked  <@" + str(id) + "> as " + str(number) + " for practice on " + date)
        else:
            conn.commit()
            cursor.close()
            conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)


def add_dummy_responses(date):
    print(date)
    member_and_id = []
    for member in get_group_info()['members']:
        if 'bot_id' not in member['profile']:
            print(member)
            member_and_id.append((member['id'], member['real_name']))
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        for slack_id, real_name in member_and_id:
            cursor.execute(sql.SQL("INSERT INTO tribe_attendance VALUES(%s, %s, -1, %s, now())"),
                           [real_name, slack_id, date])
        conn.commit()
        cursor.close()
        conn.close()
        send_debug_message("populated -1s for practice on " + date)
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message("here")
        send_debug_message(error)


def get_unanswered(date):
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL("SELECT slack_id FROM tribe_attendance WHERE \"" + date + "\" = -1"))
        unanswered = cursor.fetchall()
        print(unanswered)
        return unanswered
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)
        return []

def get_practice_attendance(date):
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE \"" + date + "\" = 1"))
        injured = cursor.fetchall()
        injured = [x[0] for x in injured]

        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE \"" + date + "\" = -1"))
        unanswered = cursor.fetchall()
        unanswered = [x[0] for x in unanswered]

        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE \"" + date + "\" = 2"))
        drills = cursor.fetchall()
        drills = [x[0] for x in drills]

        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE \"" + date + "\" = 3"))
        playing = cursor.fetchall()
        playing = [x[0] for x in playing]

        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE \"" + date + "\" = 0"))
        missing = cursor.fetchall()
        missing = [x[0] for x in missing]

        toRet = {'playing': playing, 'injured': injured, 'drills': drills, 'unanswered': unanswered, "missing": missing}
        print(toRet)
        return toRet
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)
        return {'failure': []}

def add_workout(name, slack_id, workout_type):
    cursor = None
    conn = None
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("INSERT INTO tribe_workouts VALUES (%s, %s, %s, now())"), [str(name), str(slack_id), str(workout_type)])
        conn.commit()
        send_debug_message("Committed " + name + " to the workout list")
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()

def get_workouts_after_date(date, type, slack_id):
    cursor = None
    conn = None
    workouts = []
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("SELECT * from tribe_workouts WHERE slack_id=%s and workout_date BETWEEN %s and now() and workout_type=%s"),
                       [slack_id, date, "!" + type])
        workouts = cursor.fetchall()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
    return workouts

def get_group_workouts_after_date(date, type):
    cursor = None
    conn = None
    workouts = []
    print(date, type)
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("SELECT * from tribe_workouts WHERE workout_date BETWEEN %s and now() and workout_type=%s"),
                       [date, "!" + type])
        workouts = cursor.fetchall()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
    return workouts
