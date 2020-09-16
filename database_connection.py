import os
import urllib.parse
import urllib.request
import psycopg2

from psycopg2 import sql
from slack_api import *

from flask import Flask

app = Flask(__name__)

def connect_to_db():
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
    return conn, cursor

def add_num_posts(mention_id, name):
    # "UPDATE tribe_data SET num_posts=num_posts+1, WHERE name = 'William Syre' AND last_time != "
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "UPDATE tribe_data SET num_posts=num_posts+1 WHERE slack_id = %s"),
            [mention_id[0]])
        if cursor.rowcount == 0:
            cursor.execute(sql.SQL(
                "UPDATE tribe_data SET num_posts=num_posts+1 WHERE name = %s"),
                [name])
            if cursor.rowcount == 1:
                cursor.execute(sql.SQL(
                    "UPDATE tribe_data SET slack_id = %s WHERE name = %s"),
                    [mention_id[0], name])
                send_debug_message(("%s has a new slack id" % name), level="INFO")
            else:
                cursor.execute(sql.SQL("INSERT INTO tribe_data (name, num_posts, num_workouts, workout_score, "
                                       "last_post, slack_id, active) "
                                       "VALUES (%s, 0, 0, 0, now(), %s, 't')"),
                               [name, mention_id[0]])
                send_debug_message("%s is new to Tribe" % name, level="INFO")
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        return True

def select_all():
    try:
        urllib.parse.uses_netloc.append("postgres")
        print(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
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
            "SELECT * FROM tribe_workouts"), )
        leaderboard = cursor.fetchall()
        cursor.close()
        conn.close()
        return leaderboard
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        print("error")
        print(error)
        return "RIP"

def tournaments():
    try:
        urllib.parse.uses_netloc.append("postgres")
        print(os.environ["HEROKU_POSTGRESQL_MAUVE_URL"])
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
            "SELECT * FROM tournaments"), )
        tournaments = cursor.fetchall()
        cursor.close()
        conn.close()
        return tournaments
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        print("error")
        print(error)
        return "RIP"



def collect_stats(datafield, rev):
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "SELECT * FROM tribe_data WHERE workout_score > -1.0"), )
        leaderboard = cursor.fetchall()
        leaderboard.sort(key=lambda s: s[datafield], reverse=rev)  # sort the leaderboard by score descending
        string1 = "Leaderboard:\n"
        if datafield == 7:
            for x in range(0, len(leaderboard)):
                string1 += '%d) %s with %d minutes \n' % (x + 1, leaderboard[x][0], leaderboard[x][datafield])
        else:
            for x in range(0, len(leaderboard)):
                string1 += '%d) %s with %.1f points \n' % (x + 1, leaderboard[x][0], leaderboard[x][datafield])
        cursor.close()
        conn.close()
        return string1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")


def get_group_info():
    url = "https://slack.com/api/users.list?token=" + os.getenv('BOT_OATH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json


def get_emojis():
    url = 'https://slack.com/api/emoji.list?token=' + os.getenv('OATH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json


def add_to_db(names, addition, num_workouts, ids, minutes):  # add "addition" to each of the "names" in the db
    cursor = None
    conn = None
    num_committed = 0
    committed = []
    try:
        conn, cursor = connect_to_db()
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
                cursor.execute(sql.SQL(
                    "UPDATE tribe_data SET throwing_score=throwing_score+%s, last_post="
                    "now() WHERE slack_id = %s"),
                    [str(minutes), ids[x]])
                conn.commit()
                send_debug_message("committed %s with %s points and %s minutes" % (names[x], str(addition), str(minutes)), level="INFO")
                print("committed %s with %s points and %s minutes" % (names[x], str(addition), str(minutes)))
                num_committed += 1
                committed.append((names[x], str(ids[x])))
            else:
                send_debug_message("invalid workout poster found " + names[x], level="INFO")
                num_committed += 1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error), level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return num_committed, committed

def edit_message_db(names, subtraction, num_workouts, ids, minutes):  # add "addition" to each of the "names" in the db
    cursor = None
    conn = None
    num_committed = 0
    committed = []
    try:
        conn, cursor = connect_to_db()
        for x in range(0, len(names)):
            print("starting", names[x])
            cursor.execute(sql.SQL(
                "SELECT workout_score FROM tribe_data WHERE slack_id = %s"), [str(ids[x])])
            score = cursor.fetchall()[0][0]
            score = int(score)
            if score != -1:
                cursor.execute(sql.SQL(
                    "UPDATE tribe_data SET num_workouts=num_workouts-%s, workout_score=workout_score-%s, last_post="
                    "now() WHERE slack_id = %s"),
                    [str(num_workouts), str(subtraction), ids[x]])
                cursor.execute(sql.SQL(
                    "UPDATE tribe_data SET throwing_score=throwing_score-%s, last_post="
                    "now() WHERE slack_id = %s"),
                    [str(minutes), ids[x]])
                conn.commit()
                send_debug_message("subtracted %s with %s points and %s minutes" % (names[x], str(subtraction), str(minutes)), level="INFO")
                print("subtracted %s with %s points and %s minutes" % (names[x], str(subtraction), str(minutes)))
                num_committed += 1
                committed.append((names[x], str(ids[x])))
            else:
                send_debug_message("invalid workout poster found " + names[x], level="INFO")
                num_committed += 1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error), level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return num_committed, committed


def subtract_from_db(names, subtraction, ids):  # subtract "subtraction" from each of the "names" in the db
    cursor = None
    conn = None
    num_committed = 0
    try:
        conn, cursor = connect_to_db()
        for x in range(0, len(names)):
            cursor.execute(sql.SQL(
                "UPDATE tribe_data SET workout_score = workout_score - %s WHERE slack_id = %s"),
                [subtraction, ids[x]])
            conn.commit()
            send_debug_message("subtracted %s" % names[x], level="INFO")
            num_committed += 1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return num_committed


def reteam(excluded_ids):
    info = get_group_info()
    members = [(x['id'], x['real_name']) for x in info['members'] if x['id'] != 'USLACKBOT' and not x['is_bot']]
    cursor = None
    conn = None
    try:

        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL(
            "DROP TABLE IF EXISTS tribe_data"
        ))
        cursor.execute(sql.SQL(
            "CREATE TABLE tribe_data (name text, "
            "num_posts smallint, "
            "num_workouts smallint, "
            "workout_score numeric(5,1), "
            "last_post date, "
            "slack_id varchar(11), "
            "active boolean default 't', "
            "throwing_score numeric(4, 1))"
        ))
        cursor.execute(sql.SQL("DELETE FROM tribe_workouts"))
        for member in members:
            if member[0] in excluded_ids:
                cursor.execute(sql.SQL(
                    "INSERT INTO tribe_data (name, num_posts, num_workouts, workout_score, last_post, slack_id, active)"
                    "VALUES(%s, 0, 0, -1.0, now(), %s, 't')"),
                    [member[1], member[0]]
                )
            else:
                cursor.execute(sql.SQL(
                    "INSERT INTO tribe_data (name, num_posts, num_workouts, workout_score, last_post, slack_id, active)"
                    "VALUES(%s, 0, 0, 0.0, now(), %s, 't')"),
                    [member[1], member[0]]
                )
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()


def setup():
    create_tribe_data = "create table tribe_data (name text not null constraint tribe_data_pkey primary key, num_posts smallint default 0, num_workouts   smallint      default 0, workout_score  numeric(4, 1) default 0.0, last_post date default('now':: text):: date not null, id bigint, year smallint, slack_id varchar(11), last_time integer, active boolean, throwing_score numeric(4, 1))"
    create_tribe_workouts = "create table tribe_workouts (name varchar, slack_id varchar(11), workout_type varchar, workout_date date);"
    create_tribe_poll_data = "create table tribe_poll_data (ts numeric(16, 6), slack_id varchar(11), title text, options text [], channel char(9), anonymous boolean, multi boolean, invisible boolean);"
    create_tribe_poll_responses = "create table tribe_poll_responses (ts numeric(16, 6), real_name text, slack_id varchar(11), response_num smallint);"
    create_tribe_reaction_info = "create table reaction_info (date date, yes text, no text, drills text, injured text, timestamp text);"
    create_intensity_feedback_polls = "CREATE TABLE intensity_feedback_polls (timestamp numeric(16, 6));"
    cursor = None
    conn = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL(create_tribe_data))
        cursor.execute(sql.SQL(create_tribe_workouts))
        cursor.execute(sql.SQL(create_tribe_poll_data))
        cursor.execute(sql.SQL(create_tribe_poll_responses))
        cursor.execute(sql.SQL(create_tribe_reaction_info))
        cursor.execute(sql.SQL(create_intensity_feedback_polls))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()


def reset_scores():  # reset the scores of everyone
    cursor = None
    conn = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL(
            "UPDATE tribe_data SET num_workouts = 0, workout_score = 0, num_posts = 0, last_post = now() WHERE workout_score != -1"
        ))
        cursor.execute(sql.SQL(
            "DELETE FROM tribe_workouts"
        ))
        cursor.execute(sql.SQL(
            "DELETE FROM tribe_attendance"
        ))
        cursor.execute(sql.SQL(
            "DELETE FROM reaction_info"
        ))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()


def reset_talkative():  # reset the num_posts of everyone
    cursor = None
    conn = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL(
            "UPDATE tribe_data SET num_posts = 0"))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()


def add_reaction_info_date(date, yes, drills, injured, no):
    # "UPDATE tribe_data SET num_posts=num_posts+1, WHERE name = 'William Syre' AND last_time != "
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("SELECT * FROM reaction_info WHERE date = %s"), [date])
        if cursor.rowcount == 0:
            cursor.execute(
                sql.SQL("INSERT INTO reaction_info (date, yes, no, drills, injured, timestamp) "
                        "VALUES (%s, %s, %s, %s, %s, NULL)"),
                [date.strftime("%Y-%B-%d"), yes, no, drills, injured])
            conn.commit()
            cursor.close()
            conn.close()
            print("successfully added reaction info")
            return True
        else:
            conn.commit()
            cursor.close()
            conn.close()
            send_debug_message("Found a repeat calendar post", level="DEBUG")
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")


def add_reaction_info_ts(ts):
    # "UPDATE tribe_data SET num_posts=num_posts+1, WHERE name = 'William Syre' AND last_time != "
    try:
        conn, cursor = connect_to_db()
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
        send_debug_message(error, level="ERROR")


def check_reaction_timestamp(ts):
    try:
        conn, cursor = connect_to_db()
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
        send_debug_message(error, level="ERROR")
        return []


def count_practice(slack_id, date, number):
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "UPDATE tribe_attendance SET attendance_code = %s, date_responded=now() "
            "where slack_id = %s and practice_date = %s"),
            [number, slack_id, date])
        if cursor.rowcount == 1:
            conn.commit()
            cursor.close()
            conn.close()
            send_debug_message("marked  <@" + str(slack_id) + "> as " + str(number) + " for practice on " + date, level="DEBUG")
        else:
            conn.commit()
            cursor.close()
            conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")


def add_dummy_responses(date):
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("SELECT slack_id, name FROM tribe_data WHERE active = 't'"))
        stuff = cursor.fetchall()
        print("This is the stuff")
        print(stuff)
        for slack_id, real_name in stuff:
            cursor.execute(sql.SQL("INSERT INTO tribe_attendance "
                                   "(name, slack_id, attendance_code, practice_date, date_responded) "
                                   "VALUES(%s, %s, -1, %s, now())"),
                           [real_name, slack_id, date])
        conn.commit()
        cursor.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")


def get_unanswered(date):
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "SELECT slack_id FROM tribe_attendance WHERE practice_date = %s and attendance_code = -1"),
            [date])
        unanswered = cursor.fetchall()
        print(unanswered)
        return unanswered
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        return []


def get_practice_attendance(date):
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE practice_date = %s AND attendance_code = 1"),
                       [date])
        injured = cursor.fetchall()
        injured = [x[0] for x in injured]

        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE practice_date = %s AND attendance_code = -1"),
                       [date])
        unanswered = cursor.fetchall()
        unanswered = [x[0] for x in unanswered]

        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE practice_date = %s AND attendance_code = 2"),
                       [date])
        drills = cursor.fetchall()
        drills = [x[0] for x in drills]

        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE practice_date = %s AND attendance_code = 3"),
                       [date])
        playing = cursor.fetchall()
        playing = [x[0] for x in playing]

        cursor.execute(sql.SQL("SELECT name FROM tribe_attendance WHERE practice_date = %s AND attendance_code = 0"),
                       [date])
        missing = cursor.fetchall()
        missing = [x[0] for x in missing]

        to_ret = {
            'playing': playing,
            'injured': injured,
            'drills': drills,
            'unanswered': unanswered,
            "missing": missing
        }
        print(to_ret)
        return to_ret
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        return {'failure': []}


def add_workout(name, slack_id, workout_type, img_url='NULL'):
    cursor = None
    conn = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("INSERT INTO tribe_workouts (name, slack_id, workout_type, workout_date, img_url) "
                               "VALUES (%s, %s, %s, now(), %s)"), [str(name), str(slack_id), str(workout_type), img_url])
        conn.commit()
        send_debug_message("Committed " + name + " to the workout list", level="INFO")
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()


def get_workouts_after_date(date, workout_type, slack_id):
    cursor = None
    conn = None
    workouts = []
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL(
            "SELECT * from tribe_workouts WHERE slack_id=%s and workout_date BETWEEN %s and now() and workout_type=%s"),
            [slack_id, date, "!" + workout_type])
        workouts = cursor.fetchall()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
    return workouts


def get_group_workouts_after_date(date, workout_type):
    cursor = None
    conn = None
    workouts = []
    print(date, workout_type)
    try:
        conn, cursor = connect_to_db()
        if workout_type in "all":
            if date is None:
                cursor.execute(sql.SQL(
                    "SELECT * from tribe_workouts"))
                workouts = cursor.fetchall()
            else:
                cursor.execute(sql.SQL(
                    "SELECT * from tribe_workouts WHERE workout_date BETWEEN %s and now()"),
                    [date])
                workouts = cursor.fetchall()
        else:
            if date is None:
                cursor.execute(sql.SQL(
                    "SELECT * from tribe_workouts WHERE workout_type=%s"),
                    ["!" + workout_type])
                workouts = cursor.fetchall()
            else:
                cursor.execute(sql.SQL(
                    "SELECT * from tribe_workouts WHERE workout_date BETWEEN %s and now() and workout_type=%s"),
                    [date, "!" + workout_type])
                workouts = cursor.fetchall()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
    return workouts


def get_custom_leaderboard(workout_types, date):
    cursor = None
    conn = None
    workouts = []
    print(workout_types)
    try:
        select_string = "SELECT * from tribe_workouts WHERE (workout_date BETWEEN \'" + date + "\' and now()) and ("
        for workout_type in workout_types:
            select_string += ("workout_type=%s" % ("\'!" + workout_type + "\'")) + " or "
        select_string = select_string[:-4]
        select_string += ")"
        send_debug_message(select_string, level="INFO")
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL(select_string))
        workouts = cursor.fetchall()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
    return workouts


def add_tracked_poll(title, slack_id, ts, options, channel, anonymous, multi=True, invisible=False):
    option_string = '{' + ', '.join(['\"' + x + '\"' for x in options]) + '}'
    cursor = None
    conn = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL(
            "INSERT INTO tribe_poll_data (ts, slack_id, title, options, channel, anonymous, multi, invisible)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
            [ts, slack_id, title, option_string, channel, anonymous, multi, invisible])
        conn.commit()
        send_debug_message("Committed " + title + " to the poll list", level="DEBUG")
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error), level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()


def add_poll_reaction(ts, options_number, slack_id, real_name):
    cursor = None
    conn = None
    res = 0
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("SELECT multi FROM tribe_poll_data where ts=%s"), [ts])
        multi = cursor.fetchall()[0][0]
        cursor.execute(sql.SQL(
            "SELECT * FROM tribe_poll_responses WHERE slack_id=%s AND ts=%s"),
            [slack_id, ts])
        active = cursor.rowcount >= 1
        if not active:
            return -1
        cursor.execute(sql.SQL(
            "SELECT * FROM tribe_poll_responses WHERE slack_id=%s AND ts=%s AND response_num != -1"),
            [slack_id, ts])
        num_responses = cursor.rowcount
        if multi:
            if num_responses == 0:  # they have never responded
                # delete dummy response, record response
                cursor.execute(sql.SQL(
                    "UPDATE tribe_poll_responses SET response_num = %s "
                    "WHERE slack_id=%s AND ts=%s AND response_num = -1"),
                    [options_number, slack_id, ts])
                res = 1
            elif num_responses >= 1:  # they have responded before
                # check if they are removing a response
                cursor.execute(sql.SQL(
                    "SELECT * FROM tribe_poll_responses "
                    "WHERE slack_id=%s AND ts=%s AND response_num = %s"),
                    [slack_id, ts, options_number])
                if cursor.rowcount == 0:  # they have never responded this option
                    cursor.execute(sql.SQL(
                        "INSERT INTO tribe_poll_responses (ts, slack_id, real_name, response_num) "
                        "VALUES (%s, %s, %s, %s)"),
                        [ts, slack_id, real_name, options_number])
                    res = 1
                else:  # they have responded this option so we're removing it
                    res = 0
                    if num_responses == 1:  # last response (indicate that they have no more responses)
                        cursor.execute(sql.SQL(
                            "UPDATE tribe_poll_responses SET response_num =-1 "
                            "WHERE slack_id=%s AND ts=%s AND response_num = %s"),
                            [slack_id, ts, options_number])
                    else:  # one of many responses (delete the response)
                        cursor.execute(sql.SQL(
                            "DELETE FROM tribe_poll_responses "
                            "WHERE slack_id=%s AND ts=%s AND response_num = %s"),
                            [slack_id, ts, options_number])
        else:
            cursor.execute(sql.SQL(
                "SELECT * FROM tribe_poll_responses WHERE slack_id=%s AND ts=%s AND response_num=%s"),
                [slack_id, ts, options_number])
            if cursor.rowcount == 0:
                cursor.execute(sql.SQL(
                    "UPDATE tribe_poll_responses SET response_num = %s "
                    "WHERE slack_id=%s AND ts=%s"),
                    [options_number, slack_id, ts])
                res = 1
            else:
                cursor.execute(sql.SQL(
                    "UPDATE tribe_poll_responses SET response_num = %s "
                    "WHERE slack_id=%s AND ts=%s"),
                    [-1, slack_id, ts])
                res = 0
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return res


def add_poll_dummy_responses(ts):
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("SELECT slack_id, name FROM tribe_data WHERE active ='t'"))
        stuff = cursor.fetchall()
        for slack_id, real_name in stuff:
            cursor.execute(sql.SQL(
                "INSERT INTO tribe_poll_responses (ts, real_name, slack_id, response_num) "
                "VALUES(%s, %s, %s, -1)"),
                [ts, real_name, slack_id])
        conn.commit()
        cursor.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")


def get_poll_data(ts):
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("SELECT title, options, anonymous FROM tribe_poll_data WHERE ts = %s"), [ts])
        poll_data = cursor.fetchall()
        if len(poll_data) == 0:
            return None, None, None
        title = poll_data[0][0]
        options = poll_data[0][1]
        anon = poll_data[0][2]
        cursor.execute(sql.SQL("SELECT real_name, response_num FROM tribe_poll_responses WHERE ts = %s"), [ts])
        poll_responses = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        data = {}
        if anon:
            for option in options:
                data[option] = [0]
            data['No Answer'] = [0]
            for real_name, response_num in poll_responses:
                if response_num != -1:
                    data[options[response_num]][0] += 1
                else:
                    data['No Answer'][0] += 1
        else:
            for option in options:
                data[option] = []
            data['No Answer'] = []
            for real_name, response_num in poll_responses:
                if response_num != -1:
                    data[options[response_num]].append(real_name)
                else:
                    data['No Answer'].append(real_name)

        return title, data, anon

    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        return None

def get_poll_response(slack_id, ts):
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("SELECT real_name, response_num FROM tribe_poll_responses WHERE ts = %s AND slack_id = %s"), [ts, slack_id])
        poll_responses = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        return poll_responses

    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        return None

def clear_poll_data():
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("DELETE FROM tribe_poll_responses"))
        cursor.execute(sql.SQL("DELETE FROM tribe_poll_data"))
        conn.commit()
        cursor.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")


def get_poll_unanswered(ts):
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL("SELECT slack_id FROM tribe_poll_responses WHERE ts = %s and response_num = -1"), [ts])
        unanswered = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        print(unanswered)
        return unanswered
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        return []


def get_poll_owner(ts):
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL("SELECT slack_id FROM tribe_poll_data WHERE ts = %s"),
                       [ts])
        owner = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        print(owner)
        return owner[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        return []

def get_poll_settings(ts):
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL("SELECT anonymous, multi, invisible FROM tribe_poll_data WHERE ts = %s"),
                       [ts])
        settings = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return settings[0]
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
        return []


def delete_poll(timestamp):
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("DELETE FROM tribe_poll_data WHERE ts = %s"), [timestamp])
        cursor.execute(sql.SQL("DELETE FROM tribe_poll_responses WHERE ts = %s"), [timestamp])
        conn.commit()
        cursor.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")


def delete_calendar(date):
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("DELETE FROM tribe_attendance WHERE practice_date = %s"), [date])
        cursor.execute(sql.SQL("DELETE FROM reaction_info WHERE date = %s"), [date])
        conn.commit()
        cursor.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")


def set_leaderboard_from_dict(dict: {}):
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("UPDATE tribe_data set workout_score = 0 where workout_score != -1"))
        for key in dict.keys():
            cursor.execute(sql.SQL("UPDATE tribe_data set workout_score = %s where slack_id = %s"), [dict[key], key])
        conn.commit()
        cursor.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")

def register_feedback_poll(timestamp):
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL("INSERT INTO intensity_feedback_polls (timestamp) VALUES (%s)"), [timestamp])
        conn.commit()
        cursor.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")

def get_leaderboard_total(datafield):
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        if datafield == 1:
            cursor.execute(sql.SQL(
                "SELECT workout_score FROM tribe_data WHERE workout_score > -1.0"), )
        elif datafield == 2:
            cursor.execute(sql.SQL(
                "SELECT throwing_score FROM tribe_data WHERE workout_score > -1.0"), )
        leaderboard = cursor.fetchall()
        total = 0
        for x in leaderboard:
            total += x[0]
        cursor.close()
        conn.close()
        return total
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")

def get_feedback_poll_data():
    try:
        conn, cursor = connect_to_db()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "SELECT timestamp FROM intensity_feedback_polls"))
        timestamps = cursor.fetchall()
        aggregated_poll_data = {}
        for ts in timestamps:
            title, data, anon = get_poll_data(ts[0])
            if title is not None and data is not None:
                date = title[-10:]
                aggregated_poll_data[date] = data
        cursor.close()
        conn.close()
        return aggregated_poll_data
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")

def get_image_urls():
    cursor = None
    conn = None
    urls = []
    try:
        conn, cursor = connect_to_db()
        cursor.execute(sql.SQL(
            "SELECT img_url from tribe_workouts where img_url != '' and img_url is not NULL"))
        urls = cursor.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error, level="ERROR")
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
    return urls
